"""Test to verify the test runner is working."""
import sys

def test_runner_check():
    """Simple test to verify the test runner is working."""
    print("Test runner check: Starting test...")
    assert 1 + 1 == 2, "Basic math should work"
    print("Test runner check: Test completed successfully!")

if __name__ == "__main__":
    test_runner_check()
    print("Direct execution completed successfully!")
