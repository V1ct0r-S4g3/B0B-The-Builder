"""Test that writes output to a file."""
import os
import sys
from pathlib import Path

def test_file_output():
    """Test that writes output to a file using absolute path."""
    # Use absolute path for the output file
    base_dir = Path(__file__).parent.parent
    test_output = base_dir / "test_output.txt"
    
    # Write test content
    with open(test_output, "w", encoding="utf-8") as f:
        f.write("This is a test message to file\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Current directory: {os.getcwd()}\n")
        f.write(f"Absolute path: {test_output.absolute()}\n")
        f.write("Test completed successfully!\n")
    
    # Verify file was created
    assert test_output.exists(), f"{test_output} was not created"
    
    # Read back and print the content
    with open(test_output, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Print to console for debugging
    print("Test output file content:")
    print(content)
    print("Test completed successfully!")
    
    return content
