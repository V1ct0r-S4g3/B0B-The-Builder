"""Run tests with detailed output and error reporting."""
import sys
import pytest
import traceback
from pathlib import Path
from datetime import datetime

def run_tests():
    """Run tests with detailed output and error reporting."""
    test_file = "tests/test_military_manager_extended.py"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_output/test_results_extended_{timestamp}.txt"
    
    # Create test_output directory if it doesn't exist
    Path("test_output").mkdir(exist_ok=True)
    
    print(f"Running tests from {test_file}")
    print(f"Detailed output will be saved to: {output_file}")
    
    # Run tests and capture output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Test run started at: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        
        # Run the tests
        exit_code = pytest.main([
            test_file,
            '-v',
            '--tb=long',
            '--capture=no',
            '--show-capture=all'
        ], plugins=[], stdout=f, stderr=f)
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Test run completed with exit code: {exit_code}\n")
    
    # Print the output file contents to console
    print("\nTest output:")
    print("-" * 80)
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            print(line, end='')
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
