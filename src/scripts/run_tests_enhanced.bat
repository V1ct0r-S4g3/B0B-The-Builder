@echo off
setlocal enabledelayedexpansion

:: Set the Python interpreter
set PYTHON=python

:: Create output directory if it doesn't exist
if not exist "test_output" mkdir "test_output"

:: Generate a timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=!dt:~0,4!!dt:~4,2!!dt:~6,2!_!dt:~8,2!!dt:~10,2!!dt:~12,2!"
set "output_file=test_output\test_results_!timestamp!.txt"

echo Running MilitaryManager tests...
echo Test results will be saved to: %output_file%
echo.

:: Run the test script and capture output
%PYTHON% -c "
import sys
import os
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

# Create a string buffer to capture output
output_buffer = io.StringIO()
error_buffer = io.StringIO()

# Redirect stdout and stderr
sys.stdout = output_buffer
sys.stderr = error_buffer

try:
    # Import the test module
    from tests.test_military_direct import TestMilitaryManager
    
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMilitaryManager)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    test_result = runner.run(test_suite)
    
    # Get the output
    output = output_buffer.getvalue()
    errors = error_buffer.getvalue()
    
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
    
    # Print summary to console
    print('\n' + '=' * 80)
    print('TEST SUMMARY')
    print('=' * 80)
    print(f'Tests run: {test_result.testsRun}')
    print(f'Passed: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}')
    print(f'Failed: {len(test_result.failures)}')
    print(f'Errors: {len(test_result.errors)}')
    
    if test_result.failures:
        print('\nFAILURES:' + '=' * 72)
        for i, (test, traceback_text) in enumerate(test_result.failures, 1):
            print(f'\n{i}. {test.id()}')
            print('-' * 80)
            print(traceback_text)
    
    if test_result.errors:
        print('\nERRORS:' + '=' * 74)
        for i, (test, traceback_text) in enumerate(test_result.errors, 1):
            print(f'\n{i}. {test.id()}')
            print('-' * 80)
            print(traceback_text)
    
    print('\n' + '=' * 80)
    print(f'Detailed test results saved to: {os.path.abspath(r"%output_file%")}')
    print('=' * 80)
    
    # Exit with appropriate code
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
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
"

:: Capture the exit code
set "exit_code=%ERRORLEVEL%"

:: Show the output file location
echo.
echo Test results saved to: %output_file%
echo.

:: Exit with the test result code
exit /b %exit_code%
