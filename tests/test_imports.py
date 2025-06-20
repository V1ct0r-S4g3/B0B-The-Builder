"""Test that all modules can be imported correctly."""
import unittest
import os
import sys

class TestImports(unittest.TestCase):
    """Test that all required modules can be imported."""
    
    def test_import_bot(self):
        """Test that the main bot module can be imported."""
        try:
            from src.bot.bot import CompetitiveBot
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import CompetitiveBot: {e}")
    
    def test_import_managers(self):
        """Test that all manager modules can be imported."""
        try:
            from src.managers.head_manager import HeadManager
            from src.managers.economy_manager import EconomyManager
            from src.managers.military_manager import MilitaryManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import managers: {e}")

if __name__ == "__main__":
    # Add the src directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    unittest.main()
