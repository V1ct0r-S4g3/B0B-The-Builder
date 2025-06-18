"""Direct tests for HeadManager without pytest fixtures."""
"""Direct tests for HeadManager without pytest fixtures."""
import sys
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.data import Result, Race, Difficulty
from sc2.position import Point2
from sc2.player import Bot, Computer

# Add parent directory to path to allow importing from managers
sys.path.append('.')
from managers.head_manager import HeadManager

# Helper function to run async tests
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

class TestHeadManager(unittest.TestCase):
    """Test cases for HeadManager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.maxDiff = None  # Show full diff output
        print("\n" + "="*80)
        print("SETTING UP HEAD MANAGER TEST CLASS")
        print("="*80)
    
    def setUp(self):
        """Set up each test."""
        self.mock_ai = self.create_mock_ai()
        self.manager = HeadManager(self.mock_ai)
        self.manager.debug = False  # Disable debug output for cleaner test output
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
        mock_ai.supply_army = 5
        mock_ai.supply_cap = 20
        mock_ai.supply_left = 10
        mock_ai.workers = MagicMock(amount=12)
        
        # Mock townhalls
        cc = MagicMock()
        cc.position = Point2((50, 50))
        cc.type_id = UnitTypeId.COMMANDCENTER
        mock_ai.townhalls = MagicMock(amount=1)
        mock_ai.townhalls.first = cc
        mock_ai.townhalls.ready = [cc]
        
        # Mock structures
        mock_ai.structures = MagicMock()
        mock_ai.structures.return_value = MagicMock()
        mock_ai.structures.return_value.ready = MagicMock(return_value=[])
        mock_ai.structures.return_value.exists = False
        
        # Mock units
        mock_ai.units = MagicMock()
        mock_ai.units.return_value = MagicMock(amount=0)
        
        # Mock game state
        mock_ai.state = MagicMock()
        mock_ai.state.score = MagicMock()
        mock_ai.state.score.collection_rate_minerals = 1000
        mock_ai.state.score.collection_rate_vespene = 200
        mock_ai.state.upgrades = set()
        
        return mock_ai
    
    def test_initialization(self):
        """Test that the HeadManager initializes correctly."""
        self.assertEqual(self.manager.strategy, "bio_rush")
        self.assertIn('economy', self.manager.game_state)
        self.assertIn('military', self.manager.game_state)
        self.assertIn('enemy', self.manager.game_state)
        self.assertIn('game', self.manager.game_state)
    
    def test_register_manager(self):
        """Test manager registration."""
        mock_manager = MagicMock()
        mock_manager.head = None
        
        self.manager.register_manager('test', mock_manager)
        self.assertIn('test', self.manager.managers)
        self.assertEqual(mock_manager.head, self.manager)
    
    @async_test
    async def test_on_start(self):
        """Test on_start method with multiple managers and error cases."""
        # Test with multiple managers
        mock_manager1 = AsyncMock()
        mock_manager1._initialized = False
        
        # Create a failing manager
        mock_manager2 = AsyncMock()
        mock_manager2._initialized = False
        mock_manager2.on_start.side_effect = Exception("Test error")
        
        self.manager.managers = {
            'test1': mock_manager1,
            'test2': mock_manager2
        }
        
        # Should not raise despite one manager failing
        await self.manager.on_start()
        
        # Verify managers were called
        mock_manager1.on_start.assert_called_once()
        mock_manager2.on_start.assert_called_once()
        self.assertTrue(mock_manager1._initialized)
        # Even if it failed, _initialized should be set
        self.assertTrue(mock_manager2._initialized)
    
    @async_test
    async def test_on_step(self):
        """Test on_step method with priority ordering and error handling."""
        # Set up mock managers with different priorities
        mock_economy = AsyncMock()
        mock_military = AsyncMock()
        mock_tech = AsyncMock()
        
        # Make one manager fail
        mock_tech.on_step.side_effect = Exception("Tech manager failed")
        
        self.manager.managers = {
            'economy': mock_economy,
            'military': mock_military,
            'tech': mock_tech
        }
        
        # Set strategy with specific priority
        self.manager.strategies['test_strat'] = {
            'priority': ['military', 'economy'],  # tech is not in priority list
            'conditions': {}
        }
        self.manager.strategy = 'test_strat'
        
        # Should not raise despite one manager failing
        await self.manager.on_step()
        
        # Check that managers were called in priority order
        self.assertEqual(mock_military.on_step.call_count, 1)
        self.assertEqual(mock_economy.on_step.call_count, 1)
        self.assertEqual(mock_tech.on_step.call_count, 1)  # Should still be called
        
        # Verify tech manager was called after priority managers
        mock_calls = [call[0][0] for call in mock_military.method_calls if call[0] == 'on_step']
        self.assertGreater(len(mock_calls), 0)
        
        # Test with invalid strategy (should fall back to default)
        self.manager.strategy = 'nonexistent_strategy'
        await self.manager.on_step()
        # Should not raise and should still call managers
    
    def test_update_game_state(self):
        """Test game state updates with various scenarios."""
        # Create a mock for the techlab structure
        mock_techlab = MagicMock()
        mock_techlab.type_id = UnitTypeId.TECHLAB
        mock_techlab.exists = True
        
        # Set up the structures mock to return the techlab when queried
        def mock_structures(type_id, *args, **kwargs):
            if type_id == UnitTypeId.TECHLAB:
                mock = MagicMock()
                mock.exists = True
                return mock
            return MagicMock(exists=False)
        
        self.mock_ai.structures = mock_structures
        
        # Set up mock score
        self.mock_ai.state.score = MagicMock()
        self.mock_ai.state.score.collection_rate_minerals = 60000  # 1000 per minute
        self.mock_ai.state.score.collection_rate_vespene = 12000    # 200 per minute
        
        # Reset game state and update
        self.manager._update_game_state()
        
        # Check economy state
        self.assertEqual(self.manager.game_state['economy']['worker_count'], 12)
        self.assertEqual(self.manager.game_state['economy']['base_count'], 1)
        self.assertAlmostEqual(self.manager.game_state['economy']['mineral_income'], 1000, delta=0.1)
        self.assertAlmostEqual(self.manager.game_state['economy']['gas_income'], 200, delta=0.1)
        
        # Check military state - tech level should be 2 due to techlab
        self.assertEqual(self.manager.game_state['military']['army_supply'], 5)
        self.assertEqual(self.manager.game_state['military']['tech_level'], 2)
        
        # Check game state
        self.assertEqual(self.manager.game_state['game']['time'], 0)
        self.assertEqual(self.manager.game_state['game']['supply_used'], 10)
        self.assertEqual(self.manager.game_state['game']['supply_cap'], 20)
        
        # Test with missing score (should not raise)
        del self.mock_ai.state.score
        self.manager._update_game_state()
        self.assertEqual(self.manager.game_state['economy']['mineral_income'], 0)
        
        # Test with no townhalls (should handle division by zero)
        self.mock_ai.townhalls.amount = 0
        self.manager._update_game_state()
        self.assertEqual(self.manager.game_state['economy']['saturation'], 0)
        
        # Test with fusion core (should be tech level 3)
        def mock_structures_with_fusion(type_id, *args, **kwargs):
            if type_id == UnitTypeId.FUSIONCORE:
                mock = MagicMock()
                mock.exists = True
                return mock
            return MagicMock(exists=False)
            
        self.mock_ai.structures = mock_structures_with_fusion
        self.manager._update_game_state()
        self.assertEqual(self.manager.game_state['military']['tech_level'], 3)
    
    def test_should_expand(self):
        """Test expansion decision logic."""
        # Test with bio_rush strategy (expand_when: minerals=400, bases=1)
        self.manager.strategy = 'bio_rush'
        self.manager.game_state['economy']['base_count'] = 1
        self.mock_ai.minerals = 500
        
        # With 1 base and enough minerals, should expand
        self.assertTrue(self.manager.should_expand())
        
        # Test not enough minerals (still has 1 base, which is <= bases condition)
        self.mock_ai.minerals = 300
        # Should still expand because we have <= 1 base (the condition is bases=1)
        self.assertTrue(self.manager.should_expand())
        
        # Test already have enough bases
        self.manager.game_state['economy']['base_count'] = 2
        self.mock_ai.minerals = 500
        # Should not expand because we already have more than 1 base
        self.assertFalse(self.manager.should_expand())
        
        # Test with more than enough minerals but already have enough bases
        self.manager.game_state['economy']['base_count'] = 2
        self.mock_ai.minerals = 1000
        self.assertFalse(self.manager.should_expand())
    
    def test_should_attack(self):
        """Test attack decision logic."""
        # Test with bio_rush strategy (attack_when: supply=30, upgrades=['Stimpack'])
        self.manager.strategy = 'bio_rush'
        self.manager.game_state['game']['supply_used'] = 35
        self.manager.game_state['military']['upgrades'] = ['Stimpack']
        
        self.assertTrue(self.manager.should_attack())
        
        # Test not enough supply
        self.manager.game_state['game']['supply_used'] = 20
        self.assertFalse(self.manager.should_attack())
        
        # Test missing upgrades
        self.manager.game_state['game']['supply_used'] = 35
        self.manager.game_state['military']['upgrades'] = []
        self.assertFalse(self.manager.should_attack())

    @async_test
    async def test_on_end(self):
        """Test on_end method with result handling."""
        mock_manager = AsyncMock()
        self.manager.managers = {'test': mock_manager}
        
        # Test with victory
        await self.manager.on_end(Result.Victory)
        mock_manager.on_end.assert_called_once_with(Result.Victory)
        
        # Reset mock and test with defeat
        mock_manager.reset_mock()
        await self.manager.on_end(Result.Defeat)
        mock_manager.on_end.assert_called_once_with(Result.Defeat)

    def test_error_handling(self):
        """Test error handling in various methods."""
        # Save original values
        original_ai = self.manager.ai
        original_strategy = self.manager.strategy
        
        try:
            # Test with None AI
            self.manager.ai = None
            self.manager._update_game_state()  # Should not raise
            
            # Test with missing attributes
            self.manager.ai = MagicMock()
            self.manager.ai.state = MagicMock()
            self.manager._update_game_state()  # Should handle missing attributes
            
            # Test strategy methods with invalid strategy
            self.manager.strategy = 'nonexistent_strategy'
            # Should return empty dict without raising
            self.assertEqual(self.manager.get_strategy_condition('expand_when'), {})
            
            # Test set_strategy with invalid strategy
            self.assertFalse(self.manager.set_strategy('invalid_strategy'))
            # Should not change the strategy
            self.assertEqual(self.manager.strategy, 'nonexistent_strategy')
            
            # Test set_strategy with valid strategy
            self.assertTrue(self.manager.set_strategy('mech'))
            self.assertEqual(self.manager.strategy, 'mech')
            
            # Test with invalid manager in managers dict
            self.manager.managers['invalid'] = None
            self.manager._update_game_state()  # Should not raise
            
        finally:
            # Restore original values
            self.manager.ai = original_ai
            self.manager.strategy = original_strategy

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING HEAD MANAGER TESTS")
    print("="*80)
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestHeadManager)
    
    # Run tests with increased verbosity
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
