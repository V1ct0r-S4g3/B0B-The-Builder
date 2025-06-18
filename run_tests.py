"""Test runner script using unittest with enhanced debugging."""
import unittest
import os
import sys
import importlib.util
from pathlib import Path

# Add the src directory to the Python path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_dir)

def list_python_files(directory):
    """List all Python files in the given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.py') and f != '__init__.py']

def run_tests():
    """Run tests with detailed debugging information."""
    print("=" * 80)
    print("TEST RUNNER STARTED")
    print("=" * 80)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Test directory
    test_dir = os.path.join(src_dir, 'tests')
    print(f"\nLooking for tests in: {test_dir}")
    
    # List all Python files in the test directory
    test_files = list_python_files(test_dir)
    print(f"\nFound {len(test_files)} test files:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file}")
    
    # Try to import and run each test file directly
    print("\nAttempting to run tests...")
    test_results = {}
    
    for test_file in test_files:
        module_name = os.path.splitext(test_file)[0]
        module_path = os.path.join(test_dir, test_file)
        print(f"\n{'='*40}")
        print(f"Testing: {test_file}")
        print(f"Module: {module_name}")
        print(f"Path: {module_path}")
        
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                print(f"  Error: Could not create spec for {test_file}")
                test_results[test_file] = "ERROR: Could not create spec"
                continue
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            print(f"  Successfully imported {test_file}")
            
            # If the module has a test function, run it
            if hasattr(module, 'test_addition'):
                print("  Running test_addition...")
                try:
                    module.test_addition()
                    test_results[test_file] = "PASSED"
                    print("  Test passed!")
                except Exception as e:
                    test_results[test_file] = f"FAILED: {str(e)}"
                    print(f"  Test failed: {e}")
            else:
                test_results[test_file] = "NO_TEST_FUNCTION"
                print("  No test_addition function found")
                
        except Exception as e:
            test_results[test_file] = f"IMPORT_ERROR: {str(e)}"
            print(f"  Error importing {test_file}: {e}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_file, result in test_results.items():
        print(f"{test_file}: {result}")
    
    # Return success if all tests passed
    all_passed = all("PASSED" in res for res in test_results.values() if res != "NO_TEST_FUNCTION")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_tests())
