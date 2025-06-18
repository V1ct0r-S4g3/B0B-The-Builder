"""
Test runner script for the SC2 bot tests.
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_tests():
    """Run all tests using pytest programmatically."""
    import pytest
    
    # Print Python and pytest versions
    print(f"Python {sys.version}")
    print(f"pytest {pytest.__version__}")
    
    # Run the tests
    test_dir = str(Path(__file__).parent / 'tests')
    print(f"Running tests in: {test_dir}")
    
    # List all test files
    test_files = [str(f) for f in Path(test_dir).glob('test_*.py')]
    print(f"Found test files: {test_files}")
    
    # Run pytest programmatically
    exit_code = pytest.main([
        test_dir,
        '-v',
        '--capture=no',
        '--tb=short',
    ])
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
