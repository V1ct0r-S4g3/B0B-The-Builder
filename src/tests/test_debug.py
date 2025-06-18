"""Debug test file to check pytest functionality."""
import sys
import os
from pathlib import Path

def test_debug():
    """Simple debug test."""
    print("Debug test is running!")
    assert 1 + 1 == 2

if __name__ == "__main__":
    print("Running test directly...")
    test_debug()
    print("Test completed successfully!")
