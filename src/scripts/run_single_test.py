"""Run a single test with detailed output."""
import sys
import pytest

def run_test():
    """Run a specific test with detailed output."""
    # Run a specific test with detailed output
    test_path = "tests/test_military_manager_extended.py::test_strategy_management"
    
    print(f"Running test: {test_path}")
    print("-" * 80)
    
    # Run the test with detailed output
    exit_code = pytest.main([
        test_path,
        '-v',
        '--tb=long',
        '--capture=no',
        '--show-capture=all'
    ])
    
    print("\nTest completed with exit code:", exit_code)
    return exit_code

if __name__ == "__main__":
    sys.exit(run_test())
