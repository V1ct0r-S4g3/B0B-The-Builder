"""Diagnostic test to gather information about the test environment."""
import os
import sys
import platform
import pytest

def test_environment_info():
    """Print diagnostic information about the test environment."""
    print("\n=== Environment Information ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path}")
    
    # Check if pytest is working
    print("\n=== Pytest Information ===")
    try:
        import pytest
        print(f"Pytest Version: {pytest.__version__}")
        print("Pytest Plugins:")
        for plugin in sorted(pytest._installed_plugins):
            print(f"  - {plugin}")
    except Exception as e:
        print(f"Error getting pytest info: {e}")
    
    # Check if we can import the military manager
    print("\n=== Module Import Test ===")
    try:
        from managers.military_manager import MilitaryManager
        print("Successfully imported MilitaryManager")
    except Exception as e:
        print(f"Error importing MilitaryManager: {e}")
    
    # Always pass the test
    assert True

if __name__ == "__main__":
    # This allows running the test directly with Python
    pytest.main(["-v", "-s", __file__])
