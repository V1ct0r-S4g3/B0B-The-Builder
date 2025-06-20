"""Basic tests for the CompetitiveBot class."""
import unittest
from unittest.mock import MagicMock, patch

class TestCompetitiveBot(unittest.TestCase):
    """Test cases for the CompetitiveBot class."""
    
    def setUp(self):
        """Set up the test case with a mock bot instance."""
        # Patch the BotAI class to avoid initializing the real SC2 client
        self.bot_patcher = patch('sc2.bot_ai.BotAI')
        self.mock_bot_ai = self.bot_patcher.start()
        
        # Import the bot class after patching
        from src.bot.bot import CompetitiveBot
        
        # Create a mock SC2 client
        self.mock_client = MagicMock()
        
        # Create an instance of our bot
        self.bot = CompetitiveBot()
        
        # Set up mock attributes needed by the bot
        self.bot.start_location = (0, 0)
        self.bot.enemy_race = "Terran"
        self.bot.game_started = False
        
        # Mock the head manager and its methods
        self.bot.head = MagicMock()
        self.bot.head.on_start = MagicMock()
        self.bot.head.on_step = MagicMock()
        
        # Mock other managers
        self.bot.economy_manager = MagicMock()
        self.bot.military_manager = MagicMock()
    
    def tearDown(self):
        """Clean up after each test."""
        self.bot_patcher.stop()
    
    def test_initialization(self):
        """Test that the bot initializes correctly."""
        self.assertIsNotNone(self.bot)
        self.assertIsNotNone(self.bot.head)
        self.assertIsNotNone(self.bot.economy_manager)
        self.assertIsNotNone(self.bot.military_manager)
    
    @patch('builtins.print')
    def test_on_start(self, mock_print):
        """Test the on_start method."""
        # Call on_start
        import asyncio
        asyncio.run(self.bot.on_start())
        
        # Verify the game started flag is set
        self.assertTrue(self.bot.game_started)
        
        # Verify the head manager's on_start was called
        self.bot.head.on_start.assert_called_once()
        
        # Verify the print statements
        mock_print.assert_any_call("Game started")
        mock_print.assert_any_call("Starting position: (0, 0)")
        mock_print.assert_any_call("Enemy race: Terran")
    
    @patch('builtins.print')
    def test_on_step(self, mock_print):
        """Test the on_step method."""
        # Set up the mock
        self.bot._log_game_state = MagicMock()
        
        # Call on_step
        import asyncio
        asyncio.run(self.bot.on_step(iteration=224))
        
        # Verify the head manager's on_step was called
        self.bot.head.on_step.assert_called_once()
        
        # Verify _log_game_state was called (every 224 iterations)
        self.bot._log_game_state.assert_called_once()
        
        # Test with a non-multiple of 224
        self.bot.head.on_step.reset_mock()
        self.bot._log_game_state.reset_mock()
        
        asyncio.run(self.bot.on_step(iteration=100))
        self.bot.head.on_step.assert_called_once()
        self.bot._log_game_state.assert_not_called()

if __name__ == "__main__":
    unittest.main()
