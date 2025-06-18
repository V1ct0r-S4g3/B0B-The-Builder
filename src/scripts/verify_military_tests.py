"""Final verification script for MilitaryManager tests."""
import sys
import unittest
import os
from datetime import datetime

def run_verification():
    """Run verification tests and print results."""
    print("\n" + "=" * 80)
    print("MILITARY MANAGER TEST VERIFICATION")
    print("=" * 80)
    
    # Import the test module
    try:
        from tests.test_military_direct import TestMilitaryManager
        print("✅ Successfully imported TestMilitaryManager")
    except ImportError as e:
        print(f"❌ Error importing test module: {e}")
        return 1
    
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMilitaryManager)
    
    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)
    test_result = test_runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Tests run: {test_result.testsRun}")
    print(f"Passed: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if test_result.wasSuccessful() else 1

if __name__ == "__main__":
    exit_code = run_verification()
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    sys.exit(exit_code)
