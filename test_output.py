"""Test script to verify basic Python output and functionality."""
import sys
import os

def main():
    """Main function to test basic output."""
    print("=" * 80)
    print("TEST SCRIPT STARTED")
    print("=" * 80)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Test file operations
    test_file = "test_output.txt"
    try:
        with open(test_file, "w") as f:
            f.write("Test file created successfully")
        print(f"Successfully created test file: {test_file}")
        
        with open(test_file, "r") as f:
            content = f.read()
            print(f"File content: {content}")
            
        os.remove(test_file)
        print(f"Successfully removed test file: {test_file}")
        
    except Exception as e:
        print(f"File operation failed: {e}")
    
    print("\n" + "=" * 80)
    print("TEST SCRIPT COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
