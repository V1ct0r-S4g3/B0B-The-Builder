"""
Test script to verify the test runner functionality.
"""
import unittest
import time

class TestRunnerBasic(unittest.TestCase):
    """Basic test cases for the test runner."""
    
    def test_addition(self):
        """Test basic addition."""
        self.assertEqual(1 + 1, 2)
    
    def test_subtraction(self):
        """Test basic subtraction."""
        self.assertEqual(3 - 1, 2)

class TestRunnerAdvanced(unittest.TestCase):
    """More advanced test cases for the test runner."""
    
    def test_list_operations(self):
        """Test list operations."""
        test_list = [1, 2, 3]
        test_list.append(4)
        self.assertEqual(len(test_list), 4)
        self.assertIn(4, test_list)
    
    def test_string_operations(self):
        """Test string operations."""
        test_str = "hello"
        self.assertEqual(test_str.upper(), "HELLO")
        self.assertTrue(test_str.startswith("he"))

if __name__ == "__main__":
    unittest.main()
