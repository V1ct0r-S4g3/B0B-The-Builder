"""Simple test of file writing functionality."""
import os
import sys
from datetime import datetime

def main():
    """Test file writing functionality."""
    # Create test directory if it doesn't exist
    test_dir = "test_output"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(test_dir, f"test_write_{timestamp}.txt")
    
    # Test message
    test_message = f"Test message written at {datetime.now()}\n"
    test_message += "This is a test of file writing functionality.\n"
    test_message += "If you can read this, file writing is working!\n"
    
    try:
        # Write to the file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_message)
        
        # Verify the file was written
        if os.path.exists(filename):
            print(f"SUCCESS: File written to {os.path.abspath(filename)}")
            print(f"File size: {os.path.getsize(filename)} bytes")
            return 0
        else:
            print(f"ERROR: File {filename} was not created")
            return 1
    except Exception as e:
        print(f"ERROR: Failed to write to file: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
