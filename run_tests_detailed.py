"""
Detailed test runner with enhanced output and error handling.
"""
import os
import sys
import time
import traceback
import unittest
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title: str, color: str = Colors.HEADER) -> None:
    """Print a formatted header with the given title and color."""
    print(f"\n{color}{'=' * 80}{Colors.ENDC}")
    print(f"{color}{title:^80}{Colors.ENDC}")
    print(f"{color}{'=' * 80}{Colors.ENDC}")

def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message: str) -> None:
    """Print an informational message in blue."""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def setup_environment() -> None:
    """Set up the Python environment for testing."""
    # Add the project root to the Python path
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def discover_test_files() -> List[Path]:
    """Discover all test files in the tests directory."""
    test_dir = Path(__file__).parent / 'tests'
    if not test_dir.exists():
        print_error(f"Test directory not found: {test_dir}")
        return []
    
    test_files = list(test_dir.glob('test_*.py'))
    if not test_files:
        print_warning(f"No test files found in {test_dir}")
    
    return test_files

def run_test_file(test_file: Path) -> Dict[str, Any]:
    """Run all tests in a single test file."""
    module_name = test_file.stem
    result = {
        'file': str(test_file),
        'module': module_name,
        'tests_run': 0,
        'failures': [],
        'errors': [],
        'skipped': [],
        'successful': [],
        'start_time': time.time(),
        'end_time': None,
        'duration': 0,
        'success': False
    }
    
    print_header(f"RUNNING: {module_name}", Colors.OKBLUE)
    
    try:
        # Import the test module
        import_path = f"tests.{module_name}"
        print_info(f"Importing {import_path}")
        
        # Clear any existing module from sys.modules to ensure a fresh import
        if import_path in sys.modules:
            del sys.modules[import_path]
        
        module = __import__(import_path, fromlist=['*'])
        
        # Run the tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        if suite.countTestCases() == 0:
            print_warning(f"No test cases found in {module_name}")
            result['skipped'].append("No test cases found")
            return result
        
        print_info(f"Running {suite.countTestCases()} test{'s' if suite.countTestCases() > 1 else ''}...")
        
        # Run the test suite
        runner = unittest.TextTestRunner(verbosity=2)
        test_result = runner.run(suite)
        
        # Record the results
        result['tests_run'] = test_result.testsRun
        result['failures'] = [str(f[0]) for f in test_result.failures]
        result['errors'] = [str(e[0]) for e in test_result.errors]
        result['skipped'] = [str(s[0]) for s in test_result.skipped]
        result['success'] = test_result.wasSuccessful()
        result['end_time'] = time.time()
        result['duration'] = result['end_time'] - result['start_time']
        
        if result['success']:
            print_success(f"All {result['tests_run']} tests passed in {result['duration']:.2f}s")
        else:
            print_error(f"{len(result['failures'])} failures, {len(result['errors'])} errors in {result['duration']:.2f}s")
        
        return result
        
    except Exception as e:
        error_msg = f"Error running tests in {module_name}: {str(e)}"
        print_error(error_msg)
        traceback.print_exc()
        
        result['errors'].append(error_msg)
        result['end_time'] = time.time()
        result['duration'] = result['end_time'] - result['start_time']
        result['success'] = False
        
        return result

def main() -> int:
    """Main function to run all tests."""
    start_time = time.time()
    print_header("SC2 BOT TEST RUNNER", Colors.HEADER)
    
    # Set up the environment
    setup_environment()
    
    # Discover test files
    test_files = discover_test_files()
    if not test_files:
        print_error("No test files found to run")
        return 1
    
    print_info(f"Found {len(test_files)} test file{'s' if len(test_files) > 1 else ''}:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file.name}")
    
    # Run each test file
    results = []
    for test_file in test_files:
        result = run_test_file(test_file)
        results.append(result)
    
    # Print summary
    total_tests = sum(r['tests_run'] for r in results)
    total_failures = sum(len(r['failures']) for r in results)
    total_errors = sum(len(r['errors']) for r in results)
    total_skipped = sum(len(r['skipped']) for r in results)
    total_duration = time.time() - start_time
    
    print_header("TEST SUMMARY", Colors.HEADER)
    print(f"Total test files: {len(results)}")
    print(f"Total tests run: {total_tests}")
    print(f"Total failures: {total_failures}")
    print(f"Total errors: {total_errors}")
    print(f"Total skipped: {total_skipped}")
    print(f"Total time: {total_duration:.2f}s")
    
    if total_failures == 0 and total_errors == 0:
        print_success("\nAll tests passed successfully!")
        return 0
    else:
        print_error(f"\n{total_failures + total_errors} test{'s' if (total_failures + total_errors) > 1 else ''} failed!")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
