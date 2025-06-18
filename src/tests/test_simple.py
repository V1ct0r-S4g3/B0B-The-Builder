"""Simple test to verify the test environment is working."""
import os
import sys
import unittest

class TestSimple(unittest.TestCase):
    """Test case for basic test functionality."""
    
    def test_addition(self):
        """Test basic addition."""
        print("Running test_addition...")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        result = 1 + 1
        print(f"1 + 1 = {result}")
        self.assertEqual(result, 2, f"Expected 2, got {result}")
        print("Test passed!")
    
    def test_environment(self):
        """Test that the test environment is set up correctly."""
        self.assertTrue(True, "Environment should be set up correctly")

if __name__ == "__main__":
    print("Running test_simple.py directly...")
    unittest.main()
