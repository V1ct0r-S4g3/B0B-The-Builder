"""Simplified test runner for MilitaryManager tests with file output."""
import sys
import os
import unittest
from datetime import datetime

def run_tests():
    """Run MilitaryManager tests and save results to a file."""
    # Create test output directory
    test_dir = "test_output"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(test_dir, f"military_tests_{timestamp}.txt")
    
    # Import the test module
    try:
        from tests.test_military_direct import TestMilitaryManager
    except ImportError as e:
        error_msg = f"Error importing test module: {e}"
        print(error_msg)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg + "\n")
        return 1
    
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMilitaryManager)
    
    # Run the tests and capture output
    with open(output_file, 'w', encoding='utf-8') as f:
        # Create a test runner that writes to the file
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        
        # Run the tests
        print(f"Running MilitaryManager tests. Results will be saved to: {os.path.abspath(output_file)}")
        print("-" * 80)
        
        # Run the tests and get the result
        test_result = runner.run(test_suite)
        
        # Write a summary
        f.write("\n" + "=" * 80 + "\n")
        f.write("TEST SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tests run: {test_result.testsRun}\n")
        f.write(f"Failures: {len(test_result.failures)}\n")
        f.write(f"Errors: {len(test_result.errors)}\n")
        
        # Print a summary to console
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests run: {test_result.testsRun}")
        print(f"Failures: {len(test_result.failures)}")
        print(f"Errors: {len(test_result.errors)}")
        
        if test_result.failures:
            print("\nFAILURES:" + "=" * 72)
            for i, (test, traceback_text) in enumerate(test_result.failures, 1):
                print(f"\n{i}. {test.id()}")
                print("-" * 80)
                print(traceback_text)
        
        if test_result.errors:
            print("\nERRORS:" + "=" * 74)
            for i, (test, traceback_text) in enumerate(test_result.errors, 1):
                print(f"\n{i}. {test.id()}")
                print("-" * 80)
                print(traceback_text)
        
        print("\n" + "=" * 80)
        print(f"Detailed test results saved to: {os.path.abspath(output_file)}")
        print("=" * 80)
        
        # Return 0 if all tests passed, 1 otherwise
        return 0 if test_result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
