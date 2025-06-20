"""
Environment check script with direct file output.
"""
import os
import sys
import platform
import time

def main():
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create output file with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"env_check_{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        def write_output(message):
            """Write message to both file and stdout."""
            print(message)
            f.write(f"{message}\n")
            f.flush()
        
        write_output("=" * 80)
        write_output("PYTHON ENVIRONMENT CHECK")
        write_output("=" * 80)
        write_output(f"Timestamp: {time.ctime()}")
        write_output(f"Python Executable: {sys.executable}")
        write_output(f"Python Version: {sys.version}")
        write_output(f"Platform: {platform.platform()}")
        write_output(f"Current Working Directory: {os.getcwd()}")
        write_output(f"Python Path: {sys.path}")
        
        # Test file operations
        test_file = os.path.join(output_dir, f"test_file_{timestamp}.txt")
        try:
            with open(test_file, 'w') as tf:
                tf.write("Test content")
            write_output(f"\n✓ Successfully wrote to test file: {test_file}")
            
            with open(test_file, 'r') as tf:
                content = tf.read()
            write_output(f"✓ Successfully read from test file: {content}")
            
            os.remove(test_file)
            write_output(f"✓ Successfully removed test file: {test_file}")
        except Exception as e:
            write_output(f"\n✗ Error testing file operations: {e}")
        
        # Test imports
        write_output("\nTesting imports:")
        modules = [
            'os', 'sys', 'platform', 'time', 'unittest',
            'sc2', 'numpy', 'loguru', 'pytest'
        ]
        
        for module in modules:
            try:
                __import__(module)
                write_output(f"✓ {module} imported successfully")
            except ImportError as e:
                write_output(f"✗ Failed to import {module}: {e}")
        
        # Test completion
        write_output("\nEnvironment check completed successfully!")
        write_output(f"Full output saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
