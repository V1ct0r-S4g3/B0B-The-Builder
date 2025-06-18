#!/usr/bin/env python3
"""Test script to verify bot imports and basic functionality."""
import sys
import os
import unittest
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

class TestBotImport(unittest.TestCase):
    """Test case for verifying bot imports and basic functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        cls.logger = logging.getLogger('test_bot_import')
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
    
    def test_bot_import(self):
        """Test importing and instantiating the main bot class."""
        try:
            from src.bot.bot import MyBot
            self.logger.info("Successfully imported MyBot class")
            
            # Create an instance of the bot
            bot = MyBot()
            self.logger.info("Successfully created MyBot instance")
            
            # Verify required methods exist
            required_methods = ['on_start', 'on_step', 'on_end']
            for method in required_methods:
                self.assertTrue(hasattr(bot, method), 
                              f"Bot is missing required method: {method}")
                self.logger.info("Found required method: %s", method)
            
            self.logger.info("All required methods are present")
            
        except ImportError as e:
            self.fail(f"Failed to import MyBot: {e}")
        except Exception as e:
            self.fail(f"Error creating bot instance: {e}")
    
    def test_bot_attributes(self):
        """Test that the bot has required attributes."""
        try:
            from src.bot.bot import MyBot
            bot = MyBot()
            
            # Check for required attributes
            required_attrs = ['race', 'ai_build', 'step_count']
            for attr in required_attrs:
                self.assertTrue(hasattr(bot, attr), 
                              f"Bot is missing required attribute: {attr}")
                self.logger.info("Found required attribute: %s", attr)
                
        except Exception as e:
            self.fail(f"Error testing bot attributes: {e}")
    
    def test_environment(self):
        """Test the Python environment and paths."""
        self.logger.info("Python executable: %s", sys.executable)
        self.logger.info("Python version: %s", sys.version)
        self.logger.info("Current working directory: %s", os.getcwd())
        self.logger.info("Source directory: %s", src_dir)
        
        # Verify source directory is in Python path
        self.assertIn(src_dir, sys.path, 
                     "Source directory should be in Python path")
    
    def tearDown(self):
        """Clean up after each test method."""
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main(verbosity=2)
