"""Direct tests for EconomyManager without pytest fixtures."""
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

# Add parent directory to path to allow importing from managers
sys.path.append('.')
from managers.economy_manager import EconomyManager

class TestEconomyManager(unittest.TestCase):
    """Test cases for EconomyManager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.maxDiff = None  # Show full diff output
        print("\n" + "="*80)
        print("SETTING UP ECONOMY MANAGER TEST CLASS")
        print("="*80)
    
    def setUp(self):
        """Set up each test."""
        self.mock_ai = self.create_mock_ai()
        self.manager = EconomyManager(self.mock_ai)
        print(f"\nRunning test: {self._testMethodName}")
        print("-" * 60)
    
    @staticmethod
    def create_mock_ai():
        """Create a mock AI object for testing."""
        mock_ai = MagicMock()
        mock_ai.time = 0
        mock_ai.minerals = 1000
        mock_ai.vespene = 0
        mock_ai.supply_used = 10
        mock_ai.supply_cap = 20
        mock_ai.supply_left = 10
        mock_ai.supply_workers = 10
        
        # Mock workers
        mock_ai.workers = MagicMock()
        mock_ai.workers.amount = 12
        mock_ai.workers.idle = MagicMock(return_value=[])
        mock_ai.workers.filter = MagicMock(return_value=MagicMock())
        mock_ai.workers.random = MagicMock()
        mock_ai.workers.closer_than = MagicMock(return_value=MagicMock(amount=0))
        
        # Mock townhalls
        cc = MagicMock()
        cc.position = Point2((50, 50))
        cc.is_idle = True
        cc.orders = []
        cc.type_id = UnitTypeId.COMMANDCENTER
        cc.noqueue = True
        cc.is_ready = True
        cc.is_structure = True
        cc.build_progress = 1.0
        
        mock_ai.townhalls = MagicMock()
        mock_ai.townhalls.amount = 1
        mock_ai.townhalls.first = cc
        mock_ai.townhalls.random = cc
        mock_ai.townhalls.closer_than = MagicMock(return_value=[cc])
        mock_ai.townhalls.ready = [cc]
        
        # Mock structures
        mock_ai.structures = MagicMock()
        mock_ai.structures.return_value = MagicMock()
        mock_ai.structures.return_value.ready = MagicMock(return_value=[])
        mock_ai.structures.return_value.exists = False
        mock_ai.structures.return_value.closer_than = MagicMock(return_value=MagicMock(amount=0))
        
        # Mock game methods
        mock_ai.can_afford = MagicMock(return_value=True)
        mock_ai.already_pending = MagicMock(return_value=0)
        mock_ai.select_build_worker = MagicMock(return_value=MagicMock())
        mock_ai.find_placement = MagicMock(return_value=Point2((15, 15)))
        mock_ai.distribute_workers = AsyncMock()
        
        # Mock game info
        mock_ai.game_info = MagicMock()
        mock_ai.game_info.map_center = Point2((50, 50))
        mock_ai.game_info.map_ramp = None
        mock_ai.game_info.player_start_location = Point2((10, 10))
        
        return mock_ai
    
    def test_initialization(self):
        """Test that the EconomyManager initializes correctly."""
        self.assertEqual(self.manager.worker_ratio, 16)
        self.assertEqual(self.manager.gas_workers_per_refinery, 3)
        self.assertEqual(self.manager.supply_buffer, 4)
        self.assertEqual(self.manager.expand_when_minerals, 500)
        self.assertEqual(self.manager.min_time_before_expand, 180)
    
    async def test_train_workers(self):
        """Test worker training logic."""
        # Mock the command center
        cc = self.mock_ai.townhalls.first
        cc.train = AsyncMock(return_value=True)
        
        # Test worker training when possible
        result = await self.manager.train_workers(cc)
        self.assertTrue(result)
        cc.train.assert_called_once_with(UnitTypeId.SCV, queue=False)
    
    async def test_should_build_supply_depot(self):
        """Test supply depot construction logic."""
        # Test when supply is not tight
        self.mock_ai.supply_left = 10
        self.assertFalse(await self.manager.should_build_supply_depot())
        
        # Test when supply is tight
        self.mock_ai.supply_left = 2
        self.assertTrue(await self.manager.should_build_supply_depot())
    
    async def test_should_expand(self):
        """Test expansion logic."""
        # Test when minerals are sufficient but time is too early
        self.mock_ai.minerals = 600
        self.mock_ai.time = 100
        self.assertFalse(await self.manager.should_expand())
        
        # Test when time is sufficient but minerals are low
        self.mock_ai.minerals = 300
        self.mock_ai.time = 200
        self.assertFalse(await self.manager.should_expand())
        
        # Test when conditions are met
        self.mock_ai.minerals = 600
        self.mock_ai.time = 200
        self.assertTrue(await self.manager.should_expand())
    
    async def test_manage_worker_production(self):
        """Test worker production management."""
        # Mock the train_workers method
        self.manager.train_workers = AsyncMock(return_value=True)
        
        # Test worker production
        await self.manager.manage_worker_production()
        self.manager.train_workers.assert_called_once()
    
    async def test_manage_supply_depots(self):
        """Test supply depot management."""
        # Mock the build method
        self.manager.build = AsyncMock(return_value=True)
        
        # Test when supply depot is needed
        self.mock_ai.supply_left = 2
        await self.manager.manage_supply_depots()
        self.manager.build.assert_called_once()
        
        # Reset mock and test when not needed
        self.manager.build.reset_mock()
        self.mock_ai.supply_left = 10
        await self.manager.manage_supply_depots()
        self.manager.build.assert_not_called()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING ECONOMY MANAGER TESTS")
    print("="*80)
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
