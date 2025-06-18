"""Test script to verify StarCraft II API functionality."""
import os
import sys
import unittest
import asyncio
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import SC2 modules
try:
    from sc2 import maps
    from sc2.data import Race, Difficulty
    from sc2.main import run_game
    from sc2.player import Bot, Computer
    from sc2.bot_ai import BotAI
    from sc2.sc2process import SC2Process
    SC2_AVAILABLE = True
except ImportError:
    SC2_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_sc2')

# Define test bot
class TestBot(BotAI):
    """Simple test bot for SC2 API verification."""
    
    def __init__(self):
        super().__init__()
        self.iteration = 0
    
    async def on_start(self):
        """Run on game start."""
        logger.info("Test bot started")
    
    async def on_step(self, iteration: int):
        """Run each game step."""
        self.iteration = iteration
        logger.debug("Test bot step %d", iteration)
        
        # End test after 10 iterations
        if iteration >= 10:
            logger.info("Test complete, leaving game")
            await self.client.leave()
    
    async def on_end(self, result):
        """Run when the game ends."""
        logger.info("Test bot finished with result: %s", result)

@unittest.skipIf(not SC2_AVAILABLE, "SC2 API not available")
class TestSC2API(unittest.IsolatedAsyncioTestCase):
    """Test case for StarCraft II API functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.logger = logging.getLogger('test_sc2')
        cls.map_path = "D:/Battle.net/StarCraft2/Maps"
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
    
    async def test_sc2_import(self):
        """Test that the SC2 API can be imported and used."""
        self.assertIsNotNone(maps, "Failed to import sc2.maps")
        self.assertTrue(hasattr(Race, 'Protoss'), "Race enum is missing expected values")
        self.assertTrue(hasattr(Difficulty, 'Easy'), "Difficulty enum is missing expected values")
    
    async def test_find_maps(self):
        """Test that SC2 maps can be found."""
        self.assertTrue(os.path.exists(self.map_path), 
                       f"SC2 maps directory not found at: {self.map_path}")
        
        # Check for specific map files
        map_files = []
        for root, _, files in os.walk(self.map_path):
            for file in files:
                if file.endswith(".SC2Map"):
                    map_files.append(os.path.join(root, file))
        
        self.assertGreater(len(map_files), 0, "No SC2 map files found")
        self.logger.info("Found %d map files", len(map_files))
    
    async def test_run_game(self):
        """Test running a simple game with a test bot."""
        # Skip if running in CI environment
        if os.environ.get('CI') == 'true':
            self.skipTest("Skipping SC2 game test in CI environment")
        
        # Find a map to use
        map_path = None
        for root, _, files in os.walk(self.map_path):
            for file in files:
                if file.endswith(".SC2Map") and "Automaton" in file:
                    map_path = os.path.join(root, file)
                    break
            if map_path:
                break
        
        self.assertIsNotNone(map_path, "Could not find a suitable map file")
        
        # Run the game
        result = await run_game(
            maps.get(map_path),
            [Bot(Race.Protoss, TestBot()),
             Computer(Race.Terran, Difficulty.Easy)],
            realtime=True,
            save_replay_as=os.path.join(os.getcwd(), "test_replay.SC2Replay")
        )
        
        self.assertIsNotNone(result, "Game did not return a result")
        self.logger.info("Game completed with result: %s", result)
    
    def tearDown(self):
        """Clean up after each test method."""
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main(verbosity=2)
