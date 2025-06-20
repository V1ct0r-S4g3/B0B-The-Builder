"""Simple test runner script to execute a specific test with detailed output."""
import sys
import unittest

if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING TEST WITH DETAILED OUTPUT")
    print("=" * 80)
    
    # Add the project root and src directory to the Python path
    import os
    project_root = os.path.abspath(os.path.dirname(__file__))
    src_dir = os.path.join(project_root, 'src')
    
    # Add both to sys.path if not already there
    for path in [project_root, src_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"Python path: {sys.path}")
    
    # Import the test module
    test_module = "tests.test_bot_basic"
    print(f"\nImporting test module: {test_module}")
    
    try:
        module = __import__(test_module, fromlist=['*'])
        print(f"Successfully imported {test_module}")
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        print("\n" + "-" * 80)
        print(f"Found {suite.countTestCases()} test cases")
        
        # Run the tests with a text test runner
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print("\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if not result.wasSuccessful():
            print("\nFAILURES/ERRORS:")
            for failure in result.failures + result.errors:
                print("\n" + "-" * 40)
                print(f"Test: {failure[0]}")
                print("-" * 40)
                print(failure[1])
        
    except Exception as e:
        print(f"\nERROR: Failed to run tests: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
