"""A simple test to verify test discovery and execution."""
import unittest
import os
import sys

class TestSimple(unittest.TestCase):
    """Simple test cases to verify the test environment."""
    
    def test_addition(self):
        """Test basic addition."""
        self.assertEqual(1 + 1, 2, "1 + 1 should equal 2")
    
    def test_environment(self):
        """Test the test environment setup."""
        self.assertTrue(True, "Test environment is working")
        print("Test environment check passed!")
    
    def test_import_sc2(self):
        """Test that sc2 module can be imported."""
        try:
            import sc2
            self.assertTrue(True, "sc2 module imported successfully")
            print(f"SC2 version: {sc2.__version__}")
        except ImportError as e:
            self.fail(f"Failed to import sc2 module: {e}")

if __name__ == "__main__":
    print("Running tests directly...")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    unittest.main()
