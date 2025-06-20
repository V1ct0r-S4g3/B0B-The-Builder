"""
Simple script to test Python environment and output.
"""
import os
import sys

def main():
    # Test basic output
    print("=" * 80)
    print("PYTHON ENVIRONMENT TEST")
    print("=" * 80)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Test file operations
    test_file = "test_output.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test output")
        print(f"\nSuccessfully wrote to {test_file}")
        os.remove(test_file)
        print(f"Successfully removed {test_file}")
    except Exception as e:
        print(f"\nError testing file operations: {e}")
    
    # Test imports
    print("\nTesting imports:")
    try:
        import sc2
        print("✓ sc2 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sc2: {e}")
    
    try:
        import numpy
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
    
    # Test completion
    print("\nTest script completed successfully!")

if __name__ == "__main__":
    main()
