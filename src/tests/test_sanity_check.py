"""
Sanity check tests to verify the test environment is working.
"""
import unittest

class TestSanityCheck(unittest.TestCase):
    """Test case for basic sanity checks."""
    
    def test_addition(self):
        """Test basic addition."""
        self.assertEqual(1 + 1, 2, "1 + 1 should equal 2")
    
    def test_string_upper(self):
        """Test string uppercase conversion."""
        self.assertEqual("hello".upper(), "HELLO", "String should be uppercase")
    
    def test_environment(self):
        """Test that the test environment is set up correctly."""
        self.assertTrue(True, "Environment should be set up correctly")

if __name__ == "__main__":
    unittest.main()
