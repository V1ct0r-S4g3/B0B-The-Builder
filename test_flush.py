"""
Test script with explicit output flushing to ensure visibility.
"""
import sys
import os
import time

def main():
    # Print with explicit flush
    def print_flush(*args, **kwargs):
        print(*args, **kwargs)
        sys.stdout.flush()
    
    # Test basic output with flush
    print_flush("=" * 60)
    print_flush("PYTHON OUTPUT FLUSH TEST")
    print_flush("=" * 60)
    
    # Basic info
    print_flush(f"Python Executable: {sys.executable}")
    print_flush(f"Python Version: {sys.version}")
    print_flush(f"Current Working Directory: {os.getcwd()}")
    
    # Test file operations
    test_file = "test_flush_output.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test output")
        print_flush(f"\n✓ Successfully wrote to {test_file}")
        
        with open(test_file, 'r') as f:
            content = f.read()
        print_flush(f"✓ Successfully read from {test_file}: {content}")
        
        os.remove(test_file)
        print_flush(f"✓ Successfully removed {test_file}")
    except Exception as e:
        print_flush(f"\n✗ Error testing file operations: {e}")
    
    # Test imports
    print_flush("\nTesting imports:")
    for module in ['os', 'sys', 'time', 'unittest', 'sc2', 'numpy']:
        try:
            __import__(module)
            print_flush(f"✓ {module} imported successfully")
        except ImportError as e:
            print_flush(f"✗ Failed to import {module}: {e}")
    
    # Test completion
    print_flush("\nTest script completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise
