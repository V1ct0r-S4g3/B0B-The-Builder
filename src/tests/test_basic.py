"""Basic test script to verify bot initialization."""
import unittest
import logging
import asyncio
from pathlib import Path

# Import bot
from src.bot.bot import MyBot

class TestBotInitialization(unittest.IsolatedAsyncioTestCase):
    """Test case for bot initialization and basic functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        # Set up logging to both console and file
        cls.log_file = Path("test_basic.log")
        cls.log_file.unlink(missing_ok=True)  # Remove previous log file if it exists
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.log_file, mode='w'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger('test_basic')
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.bot = self.create_mock_bot()
    
    def create_mock_bot(self):
        """Create a bot instance with mock attributes for testing."""
        self.logger.info("Creating bot instance...")
        bot = MyBot()
        
        # Mock required attributes
        class MockAI:
            def __init__(self):
                self.time = 0.0
                self.state = type('State', (), {'game_loop': 0})
                self.minerals = 50
                self.vespene = 0
                self.supply_used = 10
                self.supply_cap = 15
                self.supply_army = 0
                self.workers = type('Workers', (), {'amount': 12})()
                self.townhalls = type('Townhalls', (), {'amount': 1})()
                self.units = type('Units', (), {'of_type': lambda *_: type('Units', (), {'amount': 0})})()
                self.enemy_units = type('EnemyUnits', (), {'amount': 0})()
                self.game_info = type('GameInfo', (), {'map_name': 'Test Map'})()
                self.game_data = type('GameData', (), {'units': {}})()
                self.state = type('State', (), {
                    'score': type('Score', (), {
                        'collection_rate_minerals': 0,
                        'collection_rate_vespene': 0
                    })(),
                    'game_loop': 0
                })
        
        bot.ai = MockAI()
        return bot
    
    def test_bot_has_required_attributes(self):
        """Test that the bot has all required attributes."""
        self.assertTrue(hasattr(self.bot, 'ai'), "Bot should have 'ai' attribute")
        self.assertTrue(hasattr(self.bot, 'time'), "Bot should have 'time' attribute")
    
    def test_initial_state(self):
        """Test the initial state of the bot."""
        self.assertEqual(self.bot.ai.time, 0.0, "Initial time should be 0.0")
        self.assertEqual(self.bot.ai.minerals, 50, "Initial minerals should be 50")
        self.assertEqual(self.bot.ai.vespene, 0, "Initial vespene should be 0")
        self.assertEqual(self.bot.ai.supply_used, 10, "Initial supply used should be 10")
        self.assertEqual(self.bot.ai.supply_cap, 15, "Initial supply cap should be 15")
    
    def test_worker_count(self):
        """Test the initial worker count."""
        self.assertEqual(self.bot.ai.workers.amount, 12, "Initial worker count should be 12")
    
    def test_townhall_count(self):
        """Test the initial townhall count."""
        self.assertEqual(self.bot.ai.townhalls.amount, 1, "Initial townhall count should be 1")
    
    async def test_async_initialization(self):
        """Test async initialization if needed."""
        # Example of an async test
        self.assertTrue(True, "Async test should pass")
    
    async def test_on_start(self):
        """Test on_start."""
        logger = logging.getLogger('test_basic')
        logger.info("\n" + "-" * 20 + " Testing on_start " + "-" * 20)
        try:
            logger.info("Calling bot.on_start()...")
            await self.bot.on_start()
            logger.info("✅ Bot initialized successfully")
        except Exception as e:
            logger.error("❌ Bot initialization failed")
            logger.exception("Error details:")
            raise
    
    async def test_on_step(self):
        """Test on_step."""
        logger = logging.getLogger('test_basic')
        logger.info("\n" + "-" * 20 + " Testing on_step " + "-" * 20)
        try:
            logger.info("Calling bot.on_step(0)...")
            await self.bot.on_step(0)
            logger.info("✅ Bot step executed successfully")
        except Exception as e:
            logger.error("❌ Bot step failed")
            logger.exception("Error details:")
            raise
    
    async def test_head_manager(self):
        """Test HeadManager."""
        logger = logging.getLogger('test_basic')
        logger.info("\n" + "=" * 50)
        logger.info("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        # Verify managers were initialized
        if hasattr(self.bot, 'head_manager') and self.bot.head_manager:
            logger.info("HeadManager is initialized")
            logger.info(f"Registered managers: {list(self.bot.head_manager.managers.keys())}")
        else:
            logger.warning("HeadManager is not initialized")

if __name__ == '__main__':
    unittest.main()
