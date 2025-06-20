"""
Script to check the Python environment and test discovery.
"""
import os
import sys
import platform
import importlib
import unittest
import pkg_resources

def print_header(title, width=80):
    """Print a formatted header."""
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def check_python_environment():
    """Check Python environment details."""
    print_header("PYTHON ENVIRONMENT")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

def check_imports():
    """Check if required packages are installed."""
    print_header("REQUIRED PACKAGES")
    required = {'sc2', 'numpy', 'loguru'}  # Add other dependencies as needed
    
    for package in required:
        try:
            dist = pkg_resources.get_distribution(package)
            print(f"✓ {package}: {dist.version} (at {dist.location})")
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package}: Not installed")

def check_test_discovery():
    """Check if tests can be discovered."""
    print_header("TEST DISCOVERY")
    
    # Check if tests directory exists
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.isdir(test_dir):
        print(f"✗ Test directory not found: {test_dir}")
        return
    
    print(f"Test directory: {test_dir}")
    
    # List test files
    test_files = [f for f in os.listdir(test_dir) 
                 if f.startswith('test_') and f.endswith('.py')]
    
    if not test_files:
        print("✗ No test files found in test directory")
        return
    
    print(f"Found {len(test_files)} test files:")
    for i, test_file in enumerate(sorted(test_files), 1):
        print(f"  {i}. {test_file}")
    
    # Try to discover tests
    print("\nDiscovering tests...")
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    test_count = suite.countTestCases()
    
    if test_count == 0:
        print("✗ No test cases found in test files")
    else:
        print(f"✓ Found {test_count} test cases in {len(test_files)} files")

def main():
    """Main function to run all checks."""
    try:
        check_python_environment()
        check_imports()
        check_test_discovery()
        print("\nEnvironment check completed successfully!")
        return 0
    except Exception as e:
        print(f"\nError during environment check: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
