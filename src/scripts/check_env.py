"""Check Python environment and test execution."""
import sys
import os

def main():
    """Print environment information."""
    print("Python Environment Check")
    print("=======================")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")
    
    # Try to import pytest
    try:
        import pytest
        print(f"\nPytest Version: {pytest.__version__}")
    except ImportError:
        print("\nPytest is not installed")
    
    # Try to import asyncio
    try:
        import asyncio
        print(f"asyncio Version: {asyncio.__version__}")
    except (ImportError, AttributeError):
        print("asyncio is not available or version not accessible")
    
    # Try to import sc2
    try:
        import sc2
        print(f"SC2 Version: {sc2.__version__}")
    except (ImportError, AttributeError) as e:
        print(f"SC2 import error: {e}")

if __name__ == "__main__":
    main()
