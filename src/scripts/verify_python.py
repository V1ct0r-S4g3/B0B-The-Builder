"""Verify basic Python functionality and output."""
import os
import sys

def main():
    """Run basic tests and print results."""
    print("Python Environment Verification")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Executable: {sys.executable}")
    
    # Test basic I/O
    test_file = "verification_output.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test content written successfully!\n")
    
    if os.path.exists(test_file):
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"File I/O Test: SUCCESS - {test_file} created and read successfully")
        print(f"File content: {content.strip()}")
    else:
        print("File I/O Test: FAILED - Could not create/read test file")
    
    # Test basic functionality
    try:
        import pytest
        print(f"Pytest Version: {pytest.__version__}")
    except ImportError:
        print("Pytest is not installed")
    
    print("=" * 50)
    print("Verification complete!")

if __name__ == "__main__":
    main()
