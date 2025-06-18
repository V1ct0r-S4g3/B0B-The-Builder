"""Test file operations in the tests directory."""
import os
import sys
from pathlib import Path

def test_file_operations():
    """Test creating and reading a file in the tests directory."""
    # Create a test file in the tests directory
    test_file = Path(__file__).parent / "test_ops_output.txt"
    
    # Write test content
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test content from test_file_operations\n")
    
    # Verify the file was created
    assert test_file.exists(), f"{test_file} was not created"
    
    # Read back the content
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Print to console for debugging
    print("Test file operations completed successfully!")
    print(f"File content: {content}")
    
    return content
