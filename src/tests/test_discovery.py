"""Test file to verify test discovery."""
import unittest

class TestDiscovery(unittest.TestCase):
    """Test case for verifying test discovery."""
    
    def test_addition(self):
        """Test basic addition."""
        print("Discovery test is running!")
        self.assertEqual(1 + 1, 2, "1 + 1 should equal 2")

if __name__ == '__main__':
    unittest.main()
