"""Script to check the Python environment and test discovery."""
import sys
import os
import importlib
import unittest

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{title:^80}")
    print("=" * 80 + "\n")

def check_python_environment():
    """Check the Python environment and print information."""
    print_header("PYTHON ENVIRONMENT")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\nPython path:")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")

def check_imports():
    """Check if required modules can be imported."""
    print_header("MODULE IMPORTS")
    
    modules = [
        'sc2',
        'numpy',
        'pytest',
        'unittest'
    ]
    
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ {module_name}: {module.__file__}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")

def discover_tests():
    """Discover and list all test cases."""
    print_header("TEST DISCOVERY")
    
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Try to discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    
    print(f"Looking for tests in: {start_dir}")
    
    # List all Python files in the tests directory
    test_files = [f for f in os.listdir(start_dir) 
                 if f.startswith('test_') and f.endswith('.py')]
    
    print("\nFound test files:")
    for test_file in test_files:
        print(f"- {test_file}")
    
    # Try to load tests from each file
    print("\nAttempting to load tests:")
    for test_file in test_files:
        module_name = f"tests.{test_file[:-3]}"  # Remove .py extension
        print(f"\nLoading {module_name}...")
        try:
            module = importlib.import_module(module_name)
            tests = loader.loadTestsFromModule(module)
            print(f"  ✓ Loaded {tests.countTestCases()} test cases")
        except Exception as e:
            print(f"  ✗ Failed to load: {e}")

def main():
    """Main function to run all checks."""
    print_header("SC2 BOT TEST ENVIRONMENT CHECK")
    check_python_environment()
    check_imports()
    discover_tests()
    print_header("CHECK COMPLETE")

if __name__ == "__main__":
    main()
