import unittest
import sys
from pathlib import Path
from datetime import datetime

def run_tests():
    """Run tests using unittest and save output to a file."""
    # Create test_output directory if it doesn't exist
    Path("test_output").mkdir(exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_output/unittest_results_{timestamp}.txt"
    
    print(f"Running tests. Output will be saved to: {output_file}")
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests and capture output
    with open(output_file, 'w') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(test_suite)
    
    # Print a summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # Print the output file path
    print(f"\nDetailed output saved to: {output_file}")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
