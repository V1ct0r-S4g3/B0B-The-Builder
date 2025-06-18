@echo off
setlocal

:: Set output file path
set "OUTPUT_FILE=%USERPROFILE%\Desktop\SC2BotTestOutput.txt"

echo Running tests and saving output to: %OUTPUT_FILE%
echo ===========================================

:: Create a temporary Python script
echo import sys > %TEMP%\run_tests.py
echo import unittest >> %TEMP%\run_tests.py
echo sys.path.insert(0, r'%~dp0') >> %TEMP%\run_tests.py
echo from tests.test_economy_direct import TestEconomyManager >> %TEMP%\run_tests.py
echo. >> %TEMP%\run_tests.py
echo with open(r'%OUTPUT_FILE%', 'w') as f: >> %TEMP%\run_tests.py
echo     print('='*80, file=f) >> %TEMP%\run_tests.py
echo     print('ECONOMY MANAGER TEST OUTPUT', file=f) >> %TEMP%\run_tests.py
echo     print('='*80, file=f) >> %TEMP%\run_tests.py
echo     print('\nRunning tests...\n', file=f) >> %TEMP%\run_tests.py
echo     test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager) >> %TEMP%\run_tests.py
echo     test_runner = unittest.TextTestRunner(verbosity=2, stream=f) >> %TEMP%\run_tests.py
echo     result = test_runner.run(test_suite) >> %TEMP%\run_tests.py
echo     print('\nTest execution complete.', file=f) >> %TEMP%\run_tests.py
echo     print('Tests run: %%d, Failures: %%d, Errors: %%d' %% (result.testsRun, len(result.failures), len(result.errors)), file=f) >> %TEMP%\run_tests.py

:: Run the Python script
python %TEMP%\run_tests.py

:: Clean up
del %TEMP%\run_tests.py

echo.
echo Test execution complete.
echo Output saved to: %OUTPUT_FILE%

:: Open the output file
start notepad "%OUTPUT_FILE%"
