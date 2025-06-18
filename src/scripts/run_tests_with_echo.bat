@echo off
setlocal enabledelayedexpansion

:: Create a timestamp for the output file
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%%dt:~12,2%"
set "output_file=test_output\test_results_%timestamp%.txt"

:: Create test_output directory if it doesn't exist
if not exist "test_output" mkdir "test_output"

echo Running tests and saving output to %output_file%
echo ==================================================

:: Run the tests and save output
python -c "
import sys
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

# Redirect stdout and stderr to capture all output
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    # Import the test module
    from tests.test_military_direct import TestMilitaryManager
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMilitaryManager)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    
    # Get the output
    output = sys.stdout.getvalue()
    errors = sys.stderr.getvalue()
    
    # Print to console
    print(output)
    if errors:
        print('\nERRORS:')
        print(errors)
    
    # Write to file
    with open(r'%output_file%', 'w', encoding='utf-8') as f:
        f.write('TEST RESULTS - ')
        f.write('PASSED: {}  '.format(test_result.testsRun - len(test_result.failures) - len(test_result.errors)))
        f.write('FAILED: {}  '.format(len(test_result.failures)))
        f.write('ERRORS: {}\n\n'.format(len(test_result.errors)))
        f.write('=' * 80 + '\n')
        f.write('TEST OUTPUT\n')
        f.write('=' * 80 + '\n')
        f.write(output)
        if errors:
            f.write('\n' + '=' * 80 + '\n')
            f.write('ERRORS\n')
            f.write('=' * 80 + '\n')
            f.write(errors)
    
    # Return appropriate exit code
    sys.exit(not test_result.wasSuccessful())
    
except Exception as e:
    import traceback
    error_msg = f'Error running tests: {str(e)}\n\n{traceback.format_exc()}'
    print(error_msg, file=sys.stderr)
    with open(r'%output_file%', 'w', encoding='utf-8') as f:
        f.write('ERROR RUNNING TESTS:\n\n' + error_msg)
    sys.exit(1)
    
finally:
    # Restore stdout and stderr
    sys.stdout = old_stdout
    sys.stderr = old_stderr
"

:: Capture the exit code
set "exit_code=%ERRORLEVEL%"

:: Show the output file location
echo ==================================================
echo Test results saved to: %output_file%
echo ==================================================

:: Exit with the test result code
exit /b %exit_code%
