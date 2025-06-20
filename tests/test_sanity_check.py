"""Sanity check test to verify test discovery and execution."""
import unittest
import sys
import os
from pathlib import Path

# Debug output
print("\n" + "="*80)
print(f"Running {__file__}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print("="*80 + "\n")

class SanityCheckTest(unittest.TestCase):
    """Basic sanity check test case."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        print("\nSetting up test class...")
        # Add src to Python path if not already there
        src_dir = str(Path(__file__).parent.parent / 'src')
        if src_dir not in sys.path:
            print(f"Adding {src_dir} to Python path")
            sys.path.insert(0, src_dir)
    
    def setUp(self):
        """Set up test case."""
        print(f"\nRunning test: {self._testMethodName}")
    
    def test_imports(self):
        """Verify that imports work correctly."""
        print("\nTest: Verifying imports...")
        
        # Print current working directory and Python path for debugging
        print(f"Current working directory: {os.getcwd()}")
        print("Python path:")
        for i, path in enumerate(sys.path, 1):
            print(f"  {i}. {path}")
            
        # Try to find the bot module
        print("\nSearching for bot module...")
        import importlib.util
        
        def try_import(module_name):
            print(f"\nTrying to import {module_name}...")
            try:
                module = importlib.import_module(module_name)
                print(f"Successfully imported {module_name} from {module.__file__}")
                return module
            except ImportError as e:
                print(f"Failed to import {module_name}: {e}")
                return None
        
        # Try different import approaches
        modules_to_try = [
            'bot.bot',
            'managers.head_manager',
            'managers.economy_manager',
            'managers.military_manager',
            'src.bot.bot',
            'src.managers.head_manager',
            'src.managers.economy_manager',
            'src.managers.military_manager'
        ]
        
        for module_name in modules_to_try:
            try_import(module_name)
        
        # Try direct imports with error handling for each
        try:
            print("\nAttempting direct imports...")
            
            # Try with src prefix first
            try:
                from src.bot.bot import CompetitiveBot
                print("- Imported CompetitiveBot from src.bot.bot")
            except ImportError as e:
                print("- Failed to import CompetitiveBot from src.bot.bot")
                # Fall back to non-src path
                from bot.bot import CompetitiveBot
                print("- Imported CompetitiveBot from bot.bot")
            
            # Similar pattern for other imports
            try:
                from src.managers.head_manager import HeadManager
                print("- Imported HeadManager from src.managers.head_manager")
            except ImportError:
                from managers.head_manager import HeadManager
                print("- Imported HeadManager from managers.head_manager")
                
            try:
                from src.managers.economy_manager import EconomyManager
                print("- Imported EconomyManager from src.managers.economy_manager")
            except ImportError:
                from managers.economy_manager import EconomyManager
                print("- Imported EconomyManager from managers.economy_manager")
                
            try:
                from src.managers.military_manager import MilitaryManager
                print("- Imported MilitaryManager from src.managers.military_manager")
            except ImportError:
                from managers.military_manager import MilitaryManager
                print("- Imported MilitaryManager from managers.military_manager")
            
            print("\nAll imports succeeded!")
            self.assertTrue(True, "All imports succeeded")
            
            # Verify we can create instances
            print("\nTesting instance creation...")
            try:
                bot = CompetitiveBot()
                print("- Successfully created CompetitiveBot instance")
                self.assertTrue(hasattr(bot, 'head'), "Bot should have head manager")
                self.assertTrue(hasattr(bot, 'economy_manager'), "Bot should have economy manager")
                self.assertTrue(hasattr(bot, 'military_manager'), "Bot should have military manager")
            except Exception as e:
                print(f"- Failed to create bot instance: {e}")
                self.fail(f"Failed to create bot instance: {e}")
                
        except ImportError as e:
            print(f"\nImport error: {e}")
            print("\nCurrent sys.path:")
            for i, path in enumerate(sys.path, 1):
                print(f"  {i}. {path}")
            self.fail(f"Import failed: {e}")
    
    def test_assertion(self):
        """Simple assertion test."""
        print("\nTest: Verifying basic assertion...")
        result = 1 + 1
        print(f"1 + 1 = {result}")
        self.assertEqual(result, 2, "1 + 1 should equal 2")
        print("Assertion passed!")

if __name__ == "__main__":
    print("Running tests directly...")
    unittest.main()
