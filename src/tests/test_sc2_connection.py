"""Test script to verify StarCraft II connection and basic bot functionality."""
import os
import sys
import asyncio
import unittest
import logging
import subprocess
from pathlib import Path

# Set SC2PATH environment variable before importing SC2 modules
SC2_INSTALL_PATH = r"D:\Battle.net\StarCraft2"
os.environ['SC2PATH'] = SC2_INSTALL_PATH

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import SC2 modules
try:
    from sc2 import maps, run_game
    from sc2.data import Race, Difficulty
    from sc2.player import Bot, Computer
    from sc2.bot_ai import BotAI
    from sc2.sc2process import SC2Process
    SC2_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import SC2 modules: {e}")
    SC2_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_sc2_connection')

class TestBot(BotAI):
    """Simple test bot for SC2 connection testing."""
    
    def __init__(self):
        super().__init__()
        self.iteration = 0
        self.game_info = None
    
    async def on_start(self):
        """Run on game start."""
        self.logger = logging.getLogger('test_bot')
        self.logger.info("Test bot started")
    
    async def on_step(self, iteration: int):
        """Run each game step."""
        self.iteration = iteration
        
        # Log initial game info on first iteration
        if iteration == 0:
            self.game_info = self.game_info
            self.logger.info("Bot is running!")
            self.logger.info("Game version: %s", getattr(self, 'game_version', 'unknown'))
            self.logger.info("Map: %s", getattr(self.game_info, 'map_name', 'unknown'))
            self.logger.info("Race: %s", getattr(self, 'race', 'unknown'))
            self.logger.info("Game should now be visible in StarCraft II client")
        
        # Log progress periodically
        if iteration % 100 == 0:
            self.logger.info("Running step %d", iteration)
        
        # End test after 100 iterations in test mode
        if iteration >= 100:  # Reduced from 1000 for testing
            self.logger.info("Test complete!")
            await self.client.quit()
            return True
            
        return False
    
    async def on_end(self, result):
        """Run when the game ends."""
        self.logger.info("Test bot finished with result: %s", result)

@unittest.skipIf(not SC2_AVAILABLE, "SC2 API not available")
class TestSC2Connection(unittest.IsolatedAsyncioTestCase):
    """Test case for StarCraft II connection and basic bot functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.logger = logging.getLogger('test_sc2_connection')
        # Use the correct SC2 installation path from project configuration
        cls.sc2_install_path = r"D:\Battle.net\StarCraft2"
        cls.map_path = os.path.join(cls.sc2_install_path, "Maps")
        
        # Set SC2PATH environment variable
        os.environ['SC2PATH'] = cls.sc2_install_path
        
        # Ensure the maps directory exists
        if not os.path.exists(cls.map_path):
            raise FileNotFoundError(f"SC2 maps directory not found: {cls.map_path}")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
    
    async def test_sc2_connection(self):
        """Test that we can connect to StarCraft II and run a simple game."""
        # Skip if running in CI environment
        if os.environ.get('CI') == 'true':
            self.skipTest("Skipping SC2 game test in CI environment")
        
        # Use a simple map that should be available
        map_name = "Simple64"
        map_path = os.path.join(self.map_path, "Ladder2017Season1", f"{map_name}.SC2Map")
        
        # If the map doesn't exist in the expected location, try to find it
        if not os.path.exists(map_path):
            self.logger.warning("Map not found at expected location: %s", map_path)
            map_path = None
            for root, _, files in os.walk(self.map_path):
                if f"{map_name}.SC2Map" in files:
                    map_path = os.path.join(root, f"{map_name}.SC2Map")
                    self.logger.info("Found map at: %s", map_path)
                    break
        
        self.assertIsNotNone(map_path, f"Could not find {map_name} map file in {self.map_path}")
        self.assertTrue(os.path.exists(map_path), f"Map file does not exist: {map_path}")
        
        # Run the game
        self.logger.info("Starting test game with map: %s", map_path)
        try:
            result = await run_game(
                maps.get(map_path),
                [Bot(Race.Terran, TestBot()),
                 Computer(Race.Zerg, Difficulty.Easy)],
                realtime=True,
                save_replay_as=os.path.join(os.getcwd(), "test_connection_replay.SC2Replay")
            )
            self.assertIsNotNone(result, "Game did not return a result")
            self.logger.info("Game completed with result: %s", result)
            
        except Exception as e:
            self.logger.error("Error running game: %s", str(e), exc_info=True)
            self.fail(f"Error running game: {e}")
    
    def test_environment_variables(self):
        """Test that required environment variables are set."""
        sc2_path = os.getenv('SC2PATH')
        self.logger.info("SC2PATH: %s", sc2_path)
        self.assertIsNotNone(sc2_path, "SC2PATH environment variable is not set")
        self.assertTrue(os.path.exists(sc2_path), f"SC2PATH does not exist: {sc2_path}")
    
    def tearDown(self):
        """Clean up after each test method."""
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main(verbosity=2)
