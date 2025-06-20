"""Tests for the main bot functionality."""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock, call

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sc2.data import Race, Difficulty, AIBuild, Result
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.bot_ai import BotAI

# Import the bot class
from src.bot.bot import CompetitiveBot

# Import manager classes for proper mocking
from src.managers.head_manager import HeadManager
from src.managers.economy_manager import EconomyManager
from src.managers.military_manager import MilitaryManager

class TestCompetitiveBot(unittest.IsolatedAsyncioTestCase):
    """Test cases for the CompetitiveBot class."""

    def setUp(self):
        """Set up the test environment before each test method."""
        # Create a mock bot instance
        self.bot = CompetitiveBot()
        
        # Mock the BotAI methods and attributes
        self.bot.time = 0.0
        self.bot.state = MagicMock()
        self.bot.units = MagicMock()
        self.bot.townhalls = MagicMock()
        self.bot.workers = MagicMock()
        self.bot.game_info = MagicMock()
        self.bot.enemy_units = MagicMock()
        self.bot.enemy_structures = MagicMock()
        self.bot.supply_used = 10
        self.bot.supply_cap = 15
        self.bot.minerals = 50
        self.bot.vespene = 0
        self.bot.start_location = Point2((0, 0))
        self.bot.enemy_race = Race.Terran
        
        # Mock the head manager and other managers
        self.bot.head = AsyncMock(spec=HeadManager)
        self.bot.economy_manager = AsyncMock(spec=EconomyManager)
        self.bot.military_manager = AsyncMock(spec=MilitaryManager)
        
        # Set up the head's managers dictionary
        self.bot.head.managers = {
            'economy': self.bot.economy_manager,
            'military': self.bot.military_manager
        }
        
        # Patch the _log_game_state method
        self.bot._log_game_state = MagicMock()
        
        # Patch the distribute_workers method
        self.bot.distribute_workers = AsyncMock()

    def test_initialization(self):
        """Test that the bot initializes correctly."""
        self.assertIsInstance(self.bot, BotAI)
        self.assertIsNotNone(self.bot.head)
        self.assertIsNotNone(self.bot.economy_manager)
        self.assertIsNotNone(self.bot.military_manager)
        self.assertFalse(self.bot.game_started)
        self.assertEqual(self.bot.time, 0.0)
        self.assertIsNotNone(self.bot.state)
        self.assertIsNotNone(self.bot.units)
        self.assertIsNotNone(self.bot.townhalls)

    @patch('builtins.print')
    async def test_on_start(self, mock_print):
        """Test the on_start method initializes the game state."""
        # Call the method
        await self.bot.on_start()
        
        # Verify the game state
        self.assertTrue(self.bot.game_started)
        self.bot.head.on_start.assert_awaited_once()
        
        # Verify print statements
        mock_print.assert_any_call("Game started")
        mock_print.assert_any_call(f"Starting position: {self.bot.start_location}")
        mock_print.assert_any_call(f"Enemy race: {self.bot.enemy_race}")

    async def test_on_step(self):
        """Test the on_step method processes game steps correctly."""
        # First call (iteration 0)
        await self.bot.on_step(iteration=0)
        self.bot.head.on_step.assert_awaited_once()
        self.bot._log_game_state.assert_not_called()
        
        # Reset mocks
        self.bot.head.on_step.reset_mock()
        
        # Call again at iteration 224 (should log game state)
        await self.bot.on_step(iteration=224)
        self.bot.head.on_step.assert_awaited_once()
        self.bot._log_game_state.assert_called_once()
        
        # Reset mocks
        self.bot.head.on_step.reset_mock()
        self.bot._log_game_state.reset_mock()
        
        # Call with exception
        self.bot.head.on_step.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.bot.on_step(iteration=1)
        # Should still try to log game state if it's time
        self.bot._log_game_state.assert_not_called()

    @patch('builtins.print')
    def test_log_game_state(self, mock_print):
        """Test the _log_game_state method logs the correct information."""
        # Set up test data
        self.bot.supply_used = 30
        self.bot.supply_cap = 36
        self.bot.minerals = 200
        self.bot.vespene = 100
        
        # Mock units and structures
        mock_worker = MagicMock()
        mock_worker.type_id = UnitTypeId.SCV
        mock_worker.is_collecting = True
        mock_combat = MagicMock()
        mock_combat.type_id = UnitTypeId.MARINE
        
        self.bot.units.of_type.return_value = [mock_worker, mock_combat]
        self.bot.structures.return_value.amount = 5
        
        # Call the method
        self.bot._log_game_state()
        
        # Verify the output contains expected information
        output = "\n".join(str(call[0][0]) for call in mock_print.call_args_list)
        self.assertIn("Supply:", output)
        self.assertIn("30/36", output)
        self.assertIn("Minerals:", output)
        self.assertIn("200", output)
        self.assertIn("Vespene:", output)
        self.assertIn("100", output)
        self.assertIn("Workers:", output)
        self.assertIn("Combat Units:", output)
        self.assertIn("Structures:", output)

class TestBotIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for the bot with real SC2 components."""
    
    @patch('sc2.main.run_game')
    @patch('sc2.player.Computer')
    @patch('sc2.maps.get')
    @patch('src.bot.main.CompetitiveBot')
    @patch('builtins.print')
    async def test_bot_integration(self, mock_print, mock_bot_class, mock_map_get, mock_computer, mock_run_game):
        """Test the bot can be initialized and run in a game."""
        # Set up mocks
        mock_map = MagicMock()
        mock_map_get.return_value = mock_map
        
        # Mock the bot instance
        mock_bot = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Create and run the bot
        from src.bot.main import main
        
        # Mock the __name__ check in main()
        with patch('__main__.__name__', '__main__'):
            await main()
        
        # Verify the game was run with the correct parameters
        mock_run_game.assert_called_once()
        args, kwargs = mock_run_game.call_args
        self.assertEqual(kwargs['realtime'], False)
        
        # Verify the bot was created with the correct parameters
        mock_bot_class.assert_called_once()
        
        # Verify the bot's on_start and on_step were called
        mock_bot.on_start.assert_awaited_once()
        self.assertGreater(mock_bot.on_step.await_count, 0)

if __name__ == "__main__":
    unittest.main()
