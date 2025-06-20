"""Test script to verify test output and execution."""
import unittest
import sys
import os

class TestOutput(unittest.TestCase):
    """Test case to verify test output and execution."""
    
    def test_stdout(self):
        """Test that stdout is working correctly."""
        print("This is a test message to stdout")
        self.assertTrue(True)
    
    def test_stderr(self):
        """Test that stderr is working correctly."""
        print("This is a test message to stderr", file=sys.stderr)
        self.assertTrue(True)
    
    def test_passing(self):
        """A test that should pass."""
        self.assertEqual(1 + 1, 2)
    
    def test_failing(self):
        """A test that should fail."""
        self.assertEqual(1 + 1, 3, "This test is expected to fail")

if __name__ == "__main__":
    print("Running tests directly...")
    unittest.main()
