"""Test script to verify package installation and imports."""
import sys
import unittest
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

class TestImports(unittest.TestCase):
    """Test case for verifying package imports."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
        cls.logger = logging.getLogger('test_import')
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
    
    def test_bot_import(self):
        """Test importing the main bot module."""
        try:
            from src.bot.bot import MyBot
            self.logger.info("Successfully imported MyBot class")
            self.logger.info("Bot class: %s.%s", MyBot.__module__, MyBot.__name__)
        except ImportError as e:
            self.fail(f"Failed to import MyBot: {e}")
    
    def test_manager_imports(self):
        """Test importing manager modules."""
        try:
            from src.managers.economy_manager import EconomyManager
            from src.managers.military_manager import MilitaryManager
            from src.managers.head_manager import HeadManager
            self.logger.info("Successfully imported manager modules")
        except ImportError as e:
            self.fail(f"Failed to import manager modules: {e}")
    
    def test_script_imports(self):
        """Test importing script modules."""
        try:
            from src.scripts.simple_bot import SimpleBot
            self.logger.info("Successfully imported script modules")
        except ImportError as e:
            self.fail(f"Failed to import script modules: {e}")
    
    def test_python_environment(self):
        """Test Python environment and paths."""
        self.logger.info("Python executable: %s", sys.executable)
        self.logger.info("Python version: %s", sys.version)
        self.logger.info("Python path:")
        for i, path in enumerate(sys.path, 1):
            self.logger.info("%d. %s", i, path)
        
        self.assertIn(src_dir, sys.path, "Source directory should be in Python path")
    
    def tearDown(self):
        """Clean up after each test method."""
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main()
