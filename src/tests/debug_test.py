"""Debug test script to verify test environment."""
import sys
import os

def test_environment():
    """Test basic Python environment."""
    print("Python version:", sys.version)
    print("Current directory:", os.getcwd())
    print("Files in tests directory:", os.listdir('.'))
    assert 1 + 1 == 2

if __name__ == "__main__":
    test_environment()
