"""Tests for the HeadManager class."""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sc2.data import Race, Result
from sc2.ids.unit_typeid import UnitTypeId

# Import the manager to test
from src.managers.head_manager import HeadManager

class TestHeadManager(unittest.IsolatedAsyncioTestCase):
    """Test cases for the HeadManager class."""

    async def asyncSetUp(self):
        """Set up the test environment before each test method."""
        # Create a mock AI object
        self.ai = MagicMock()
        self.ai.time = 0.0
        self.ai.minerals = 50
        self.ai.vespene = 0
        self.ai.supply_used = 10
        self.ai.supply_cap = 15
        
        # Create the manager instance
        self.manager = HeadManager(self.ai, strategy="bio_rush", debug=True)
        
        # Mock managers
        self.economy_manager = AsyncMock()
        self.military_manager = AsyncMock()
        
        # Register mock managers
        self.manager.register_manager('economy', self.economy_manager)
        self.manager.register_manager('military', self.military_manager)

    async def test_initialization(self):
        """Test that the HeadManager initializes correctly."""
        self.assertEqual(self.manager.strategy, "bio_rush")
        self.assertTrue(self.manager.debug)
        self.assertFalse(self.manager._initialized)
        self.assertEqual(self.manager._step_count, 0)
        self.assertIn('economy', self.manager.managers)
        self.assertIn('military', self.manager.managers)

    async def test_register_manager(self):
        """Test manager registration."""
        # Test registering a new manager
        test_manager = AsyncMock()
        self.manager.register_manager('test', test_manager)
        self.assertIn('test', self.manager.managers)
        self.assertEqual(self.manager.managers['test'], test_manager)
        
        # Test that the manager's head reference is set
        self.assertEqual(test_manager.head, self.manager)

    async def test_on_start(self):
        """Test the on_start method initializes all managers."""
        await self.manager.on_start()
        
        # Verify all managers were initialized
        self.economy_manager.on_start.assert_awaited_once()
        self.military_manager.on_start.assert_awaited_once()
        self.assertTrue(self.manager._initialized)

    async def test_on_step(self):
        """Test the on_step method updates all managers."""
        # First call on_start to initialize
        await self.manager.on_start()
        
        # Reset mocks to isolate on_step testing
        self.economy_manager.reset_mock()
        self.military_manager.reset_mock()
        
        # Call on_step
        await self.manager.on_step()
        
        # Verify all managers were updated
        self.economy_manager.on_step.assert_awaited_once()
        self.military_manager.on_step.assert_awaited_once()
        self.assertEqual(self.manager._step_count, 1)

    async def test_get_manager(self):
        """Test retrieving a manager by name."""
        # Test getting existing manager
        economy = self.manager.get_manager('economy')
        self.assertEqual(economy, self.economy_manager)
        
        # Test getting non-existent manager
        with self.assertRaises(KeyError):
            self.manager.get_manager('nonexistent')

    async def test_strategy_management(self):
        """Test strategy management methods."""
        # Test setting a new strategy
        self.manager.set_strategy("tank_push")
        self.assertEqual(self.manager.strategy, "tank_push")
        
        # Test getting current strategy
        current_strategy = self.manager.get_strategy()
        self.assertEqual(current_strategy, "tank_push")

    async def test_game_state_tracking(self):
        """Test game state tracking functionality."""
        # Test updating game state
        self.manager.update_game_state('economy', 'minerals', 500)
        self.assertEqual(self.manager.game_state['economy']['minerals'], 500)
        
        # Test getting game state
        minerals = self.manager.get_game_state('economy', 'minerals')
        self.assertEqual(minerals, 500)
        
        # Test getting non-existent state
        with self.assertRaises(KeyError):
            self.manager.get_game_state('nonexistent', 'value')

    async def test_handle_game_end(self):
        """Test game end handling."""
        # Test with victory
        await self.manager.handle_game_end(Result.Victory)
        self.economy_manager.on_game_end.assert_called_once_with(Result.Victory)
        self.military_manager.on_game_end.assert_called_once_with(Result.Victory)
        
        # Reset mocks
        self.economy_manager.reset_mock()
        self.military_manager.reset_mock()
        
        # Test with defeat
        await self.manager.handle_game_end(Result.Defeat)
        self.economy_manager.on_game_end.assert_called_once_with(Result.Defeat)
        self.military_manager.on_game_end.assert_called_once_with(Result.Defeat)

if __name__ == "__main__":
    unittest.main()
