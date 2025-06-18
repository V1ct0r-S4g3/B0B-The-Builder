"""Run MilitaryManager tests with direct console output."""
import sys
import unittest
import io
from contextlib import redirect_stdout, redirect_stderr

def run_tests():
    """Run tests and print results to console."""
    print("=" * 80)
    print("RUNNING MILITARY MANAGER TESTS")
    print("=" * 80)
    
    # Import the test module
    try:
        from tests.test_military_direct import TestMilitaryManager
    except ImportError as e:
        print(f"Error importing test module: {e}")
        return 1
    
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMilitaryManager)
    
    # Create a string buffer to capture output
    output_buffer = io.StringIO()
    
    # Run the tests with output captured
    with redirect_stdout(output_buffer):
        with redirect_stderr(output_buffer):
            runner = unittest.TextTestRunner(verbosity=2, stream=output_buffer)
            test_result = runner.run(test_suite)
    
    # Print the captured output
    print(output_buffer.getvalue())
    
    # Print a summary
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
    print("TEST EXECUTION COMPLETE")
    print("=" * 80)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if test_result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
