"""Run extended military manager tests using unittest framework."""
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2
from managers.military_manager import MilitaryManager

class TestMilitaryManager(unittest.TestCase):
    """Test cases for MilitaryManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai = MagicMock()
        self.mock_ai.time = 0
        self.mock_ai.minerals = 1000
        self.mock_ai.vespene = 0
        self.mock_ai.supply_used = 10
        self.mock_ai.supply_cap = 20
        self.mock_ai.supply_left = 10
        self.mock_ai.units = MagicMock()
        self.mock_ai.structures = MagicMock()
        self.mock_ai.townhalls = MagicMock()
        self.mock_ai.enemy_units = []
        self.mock_ai.enemy_structures = []
        self.mock_ai.game_info = MagicMock()
        self.mock_ai.game_info.map_center = Point2((50, 50))
        self.manager = MilitaryManager(self.mock_ai)
    
    def test_strategy_management(self):
        """Test strategy management."""
        print("\nTesting strategy management...")
        # Test default strategy
        self.assertEqual(self.manager.strategy, "bio_rush")
        
        # Test changing strategy
        self.manager.set_strategy("tank_push")
        self.assertEqual(self.manager.strategy, "tank_push")
        
        # Test invalid strategy falls back to default
        self.manager.set_strategy("invalid_strategy")
        self.assertEqual(self.manager.strategy, "bio_rush")
        print("✅ Strategy management tests passed")
    
    async def test_async_unit_production(self):
        """Test unit production logic."""
        print("\nTesting unit production...")
        # Mock barracks
        mock_barracks = MagicMock()
        mock_barracks.is_ready = True
        mock_barracks.is_idle = True
        mock_barracks.train = AsyncMock(return_value=True)
        self.mock_ai.structures.return_value = [mock_barracks]
        
        # Test marine production
        self.mock_ai.can_afford.return_value = True
        self.mock_ai.already_pending.return_value = 0
        
        # Call the method that triggers unit production
        self.mock_ai.units.return_value = []
        await self.manager._train_units()
        
        # Verify marine was trained
        mock_barracks.train.assert_called_once_with(UnitTypeId.MARINE)
        print("✅ Unit production tests passed")

if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(TestMilitaryManager('test_strategy_management'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run async tests
    async def run_async_tests():
        print("\nRunning async tests...")
        tester = TestMilitaryManager()
        tester.setUp()
        await tester.test_async_unit_production()
    
    asyncio.run(run_async_tests())
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
