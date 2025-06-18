"""Unit tests for SC2 bot functionality and environment."""
import os
import sys
import platform
import unittest
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_sc2_bot')

class TestSC2Bot(unittest.TestCase):
    """Test case for SC2 bot functionality and environment."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.output_file = Path("test_sc2_bot_output.txt")
        if cls.output_file.exists():
            cls.output_file.unlink()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger = logging.getLogger(f"test_sc2_bot.{self._testMethodName}")
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
        self._log(f"\n{'=' * 50}")
        self._log(f"TEST: {self._testMethodName}")
        self._log(f"{'=' * 50}")
    
    def _log(self, message):
        """Log a message to file and console."""
        self.logger.info(message)
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
        except Exception as e:
            self.logger.error("Error writing to log file: %s", e)
    
    def test_environment_info(self):
        """Test environment information is accessible."""
        self._log(f"Python: {sys.executable}")
        self._log(f"Version: {sys.version}")
        self._log(f"Platform: {platform.platform()}")
        self._log(f"Current directory: {os.getcwd()}")
        
        # Basic environment checks
        self.assertTrue(isinstance(sys.executable, str), "Python executable path should be a string")
        self.assertTrue(os.path.isabs(sys.executable), "Python executable path should be absolute")
    
    def test_sc2_import(self):
        """Test that the SC2 module can be imported."""
        try:
            import sc2
            self._log(f"✅ sc2 module imported successfully")
            self._log(f"sc2 version: {sc2.__version__}")
            self.assertIsNotNone(sc2.__version__, "SC2 version should be available")
        except ImportError as e:
            self.fail(f"Failed to import sc2 module: {e}")
    
    def test_bot_import(self):
        """Test that the bot module can be imported."""
        try:
            from bot.bot import MyBot
            self._log("✅ Bot module imported successfully")
            self._log(f"Bot class: {MyBot.__name__}")
            
            # Test creating bot instance
            bot = MyBot()
            self.assertIsNotNone(bot, "Failed to create bot instance")
            self._log("✅ Bot instance created successfully")
            
            # Test required methods
            required_methods = ['on_start', 'on_step', 'on_end']
            for method in required_methods:
                self.assertTrue(hasattr(bot, method), 
                             f"Bot is missing required method: {method}")
                self._log(f"✅ Found required method: {method}")
                
        except Exception as e:
            self.fail(f"Error during bot import/initialization: {e}")
    
    def test_sc2_map_directory(self):
        """Test that the SC2 map directory exists and contains maps."""
        map_dir = "D:/Battle.net/StarCraft2/Maps"
        self._log(f"Checking SC2 maps directory: {map_dir}")
        
        self.assertTrue(os.path.exists(map_dir), 
                       f"SC2 maps directory not found: {map_dir}")
        
        # List some maps
        map_files = []
        for root, _, files in os.walk(map_dir):
            for file in files:
                if file.endswith(".SC2Map"):
                    map_files.append(os.path.join(root, file))
                    if len(map_files) >= 5:  # Limit to 5 maps
                        break
            if len(map_files) >= 5:
                break
        
        self._log("\nFound maps:")
        for map_file in map_files[:5]:  # Log first 5 maps
            self._log(f"- {map_file}")
        
        self.assertGreaterEqual(len(map_files), 1, 
                              "No SC2 map files found in the maps directory")
    
    def tearDown(self):
        """Clean up after each test method."""
        self._log(f"{'=' * 50}")
        self._log("TEST COMPLETED")
        self._log(f"{'=' * 50}\n")
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main(verbosity=2)
