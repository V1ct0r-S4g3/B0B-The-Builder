"""Direct test runner for HeadManager tests."""
import sys
import unittest
import asyncio
import os
from pathlib import Path

# Add the tests directory to the path
sys.path.append('.')

# Import the test case
from tests.test_head_direct import TestHeadManager

async def run_tests():
    """Run the HeadManager tests and save output to a file."""
    print("\n" + "="*80)
    print("RUNNING HEAD MANAGER TESTS")
    print("="*80)
    
    # Create output directory if it doesn't exist
    output_dir = Path.home() / 'Desktop' / 'SC2BotTestOutput'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'head_manager_test_results.txt'
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestHeadManager)
    
    # Run tests and capture output
    with open(output_file, 'w', encoding='utf-8') as f:
        print('=' * 80, file=f)
        print('HEAD MANAGER TEST OUTPUT', file=f)
        print('=' * 80, file=f)
        print('\nRunning tests...\n', file=f)
        
        # Create test runner
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        
        # Run tests
        result = runner.run(test_suite)
        
        # Print summary
        print('\nTest execution complete.', file=f)
        print(f'Tests run: {result.testsRun}', file=f)
        print(f'Failures: {len(result.failures)}', file=f)
        print(f'Errors: {len(result.errors)}', file=f)
    
    # Show success message
    print("\nTest execution complete.")
    print(f"Output saved to: {output_file}")
    
    # Open the file in notepad
    try:
        os.startfile(str(output_file))
    except Exception as e:
        print(f"Could not open file automatically: {e}")
    
    return not result.wasSuccessful()

if __name__ == "__main__":
    # Run the async test function
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
