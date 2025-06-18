"""Test writing to temporary directory."""
import os
import tempfile
from pathlib import Path

def test_temp_dir():
    """Test writing to temporary directory."""
    # Get the temp directory
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / "sc2_bot_test.txt"
    
    # Write test content
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test content written to temp directory\n")
    
    # Verify file was created
    assert test_file.exists(), f"{test_file} was not created"
    
    # Read back the content
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Print file path for debugging
    print(f"Test file created at: {test_file}")
    print(f"File content: {content.strip()}")
    
    # Clean up
    test_file.unlink()
    
    return str(test_file)
