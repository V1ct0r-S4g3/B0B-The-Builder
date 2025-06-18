"""Simple test to verify test execution."""
import unittest
import sys

class TestHello(unittest.TestCase):
    """Test case for basic test execution."""
    
    def test_hello(self):
        """Test that prints a message and asserts True."""
        print("HELLO FROM TEST")
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
