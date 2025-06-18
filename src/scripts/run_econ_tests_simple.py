"""Simple script to run EconomyManager tests and save output."""
import sys
import unittest
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the test case
from tests.test_economy_direct import TestEconomyManager

def main():
    """Run tests and save output to file."""
    # Create output directory if it doesn't exist
    output_dir = Path.home() / 'Desktop'
    output_file = output_dir / 'SC2BotTestOutput.txt'
    
    print(f"Running EconomyManager tests and saving output to: {output_file}")
    print("=" * 80)
    
    # Run tests and capture output
    with open(output_file, 'w', encoding='utf-8') as f:
        print('=' * 80, file=f)
        print('ECONOMY MANAGER TEST OUTPUT', file=f)
        print('=' * 80, file=f)
        print('\nRunning tests...\n', file=f)
        
        # Create test suite and runner
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager)
        test_runner = unittest.TextTestRunner(stream=f, verbosity=2)
        
        # Run tests
        result = test_runner.run(test_suite)
        
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
        import os
        os.startfile(str(output_file))
    except Exception as e:
        print(f"Could not open file automatically: {e}")

if __name__ == "__main__":
    main()
