@echo off
setlocal

:: Set output file path
set "OUTPUT_FILE=%USERPROFILE%\\Desktop\\SC2BotTestOutput.txt"

echo Running tests and saving output to: %OUTPUT_FILE%
echo ===========================================

:: Run tests and save output
python -c "
import sys
import unittest
from tests.test_economy_direct import TestEconomyManager

# Redirect stdout to file
with open(r'%OUTPUT_FILE%', 'w') as f:
    # Save original stdout
    original_stdout = sys.stdout
    sys.stdout = f
    
    print('='*80)
    print('ECONOMY MANAGER TEST OUTPUT')
    print('='*80)
    
    # Run tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager)
    test_runner = unittest.TextTestRunner(verbosity=2, stream=f)
    test_runner.run(test_suite)
    
    # Restore original stdout
    sys.stdout = original_stdout
"

echo Test execution complete.
echo Output saved to: %OUTPUT_FILE%

:: Open the output file
start notepad "%OUTPUT_FILE%"
