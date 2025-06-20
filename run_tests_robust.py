"""
Robust test runner for the SC2 Bot project.

This script provides a more reliable way to run tests across different environments.
It includes better error handling and output formatting.
"""
import os
import sys
import time
import unittest
import traceback
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

class TestResult:
    """Class to track test results."""
    def __init__(self):
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.test_cases = []
    
    def add_test_case(self, name: str, status: str, message: str = "", duration: float = 0.0) -> None:
        """Add a test case result."""
        self.test_cases.append({
            'name': name,
            'status': status,
            'message': message,
            'duration': duration
        })
        
        self.total_tests += 1
        if status == 'PASSED':
            self.passed += 1
        elif status == 'FAILED':
            self.failed += 1
        elif status == 'ERROR':
            self.errors += 1
        elif status == 'SKIPPED':
            self.skipped += 1
    
    def print_summary(self) -> None:
        """Print a summary of test results."""
        print_header("TEST SUMMARY", Colors.HEADER)
        
        # Print overall stats
        print(f"{Colors.BOLD}Total Tests:{Colors.ENDC} {self.total_tests}")
        print(f"{Colors.OKGREEN}✓ Passed:{Colors.ENDC} {self.passed}")
        print(f"{Colors.FAIL}✗ Failed:{Colors.ENDC} {self.failed}")
        print(f"{Colors.WARNING}⚠ Errors:{Colors.ENDC} {self.errors}")
        print(f"{Colors.OKBLUE}↷ Skipped:{Colors.ENDC} {self.skipped}")
        
        # Print detailed results
        if self.test_cases:
            print("\nDetailed Results:")
            for test in self.test_cases:
                status_color = Colors.OKGREEN if test['status'] == 'PASSED' else \
                              Colors.FAIL if test['status'] in ('FAILED', 'ERROR') else \
                              Colors.WARNING
                
                status_text = f"{status_color}{test['status']:8s}{Colors.ENDC}"
                duration_text = f"{test['duration']:.3f}s" if test['duration'] > 0 else ""
                print(f"  {status_text} {test['name']} {duration_text}")
                if test['message']:
                    print(f"     {test['message']}")

def run_tests() -> int:
    """
    Run all tests in the tests directory.
    
    Returns:
        int: 0 if all tests passed, 1 otherwise
    """
    start_time = time.time()
    print_header("SC2 BOT TEST RUNNER", Colors.HEADER)
    
    # Set up paths
    project_root = os.path.abspath(os.path.dirname(__file__))
    test_dir = os.path.join(project_root, 'tests')
    
    # Add project root to Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Initialize test results
    test_results = TestResult()
    
    # Check if test directory exists
    if not os.path.isdir(test_dir):
        print_error(f"Test directory not found: {test_dir}")
        return 1
    
    # Discover test files
    test_files = []
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print_error("No test files found!")
        return 1
    
    # Sort test files for consistent ordering
    test_files.sort()
    
    print_info(f"Found {len(test_files)} test files:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i:2d}. {os.path.relpath(test_file, project_root)}")
    
    # Run tests
    print_header("RUNNING TESTS", Colors.OKBLUE)
    
    # Set up test loader and runner
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=2)
    
    for test_file in test_files:
        module_start_time = time.time()
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        module_display_name = module_name.replace('_', ' ').title()
        
        print_header(f"TEST MODULE: {module_display_name}", Colors.OKCYAN)
        print(f"File: {os.path.relpath(test_file, project_root)}")
        
        try:
            # Import the test module
            print_info(f"Importing test module: {module_name}")
            
            # Calculate the module path relative to the project root
            rel_path = os.path.relpath(test_file, project_root)
            module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
            
            # Import the module
            try:
                module = __import__(module_path, fromlist=['*'])
                print_success(f"Successfully imported {module_name}")
            except Exception as e:
                error_msg = f"Error importing {module_name}: {str(e)}"
                print_error(error_msg)
                test_results.add_test_case(module_name, 'ERROR', error_msg)
                continue
            
            # Discover and run tests
            try:
                print_info(f"Discovering tests in {module_name}...")
                test_suite = loader.loadTestsFromModule(module)
                test_count = test_suite.countTestCases()
                
                if test_count == 0:
                    print_warning(f"No test cases found in {module_name}")
                    test_results.add_test_case(module_name, 'SKIPPED', "No test cases found")
                    continue
                
                print_info(f"Running {test_count} test{'s' if test_count > 1 else ''}...")
                result = runner.run(test_suite)
                
                # Record test results
                duration = time.time() - module_start_time
                
                # Process test results
                for test_case in result.passed:
                    test_results.add_test_case(
                        f"{module_name}.{test_case._testMethodName}",
                        'PASSED',
                        duration=duration
                    )
                
                for test_case, trace in result.failures + result.errors:
                    test_name = f"{module_name}.{test_case._testMethodName}"
                    if test_case in result.errors:
                        status = 'ERROR'
                        message = f"Error: {trace.splitlines()[-1]}"
                    else:
                        status = 'FAILED'
                        message = f"Failure: {trace.splitlines()[-1]}"
                    
                    test_results.add_test_case(
                        test_name,
                        status,
                        message,
                        duration=duration
                    )
                
                for test_case, reason in result.skipped:
                    test_results.add_test_case(
                        f"{module_name}.{test_case._testMethodName}",
                        'SKIPPED',
                        f"Skipped: {reason}",
                        duration=duration
                    )
                
            except Exception as e:
                error_msg = f"Error running tests in {module_name}: {str(e)}"
                print_error(error_msg)
                test_results.add_test_case(module_name, 'ERROR', error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error processing {module_name}: {str(e)}"
            print_error(error_msg)
            test_results.add_test_case(module_name, 'ERROR', error_msg)
        
        # Print module execution time
        module_duration = time.time() - module_start_time
        print_info(f"Module completed in {module_duration:.2f} seconds")
    
    # Calculate total execution time
    total_duration = time.time() - start_time
    
    # Print final summary
    test_results.print_summary()
    
    # Print execution time
    print(f"\n{Colors.BOLD}Total execution time:{Colors.ENDC} {total_duration:.2f} seconds")
    
    # Return appropriate exit code
    if test_results.failed > 0 or test_results.errors > 0:
        print_error("\nSome tests failed!")
        return 1
    
    if test_results.passed == 0 and test_results.total_tests > 0:
        print_warning("\nNo tests were executed!")
        return 1
    
    print_success("\nAll tests passed successfully!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(run_tests())
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
