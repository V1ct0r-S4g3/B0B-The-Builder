@echo off
setlocal

:: Set output file path
set "OUTPUT_FILE=%USERPROFILE%\Desktop\SC2BotTestOutput.txt"

echo Running EconomyManager tests and saving output to: %OUTPUT_FILE%
echo =========================================================

:: Create a temporary Python script
echo import sys > %TEMP%\econ_tests.py
echo import unittest >> %TEMP%\econ_tests.py
echo sys.path.insert(0, 'D:\\SC2 Bot\\B0B') >> %TEMP%\econ_tests.py
echo from tests.test_economy_direct import TestEconomyManager >> %TEMP%\econ_tests.py
echo. >> %TEMP%\econ_tests.py
echo with open(r'%OUTPUT_FILE%', 'w') as f: >> %TEMP%\econ_tests.py
echo     print('='*80, file=f) >> %TEMP%\econ_tests.py
echo     print('ECONOMY MANAGER TEST OUTPUT', file=f) >> %TEMP%\econ_tests.py
echo     print('='*80, file=f) >> %TEMP%\econ_tests.py
echo     print('\nRunning tests...\n', file=f) >> %TEMP%\econ_tests.py
echo     test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager) >> %TEMP%\econ_tests.py
echo     test_runner = unittest.TextTestRunner(verbosity=2, stream=f) >> %TEMP%\econ_tests.py
echo     result = test_runner.run(test_suite) >> %TEMP%\econ_tests.py
echo     print('\nTest execution complete.', file=f) >> %TEMP%\econ_tests.py
echo     print('Tests run: %%d, Failures: %%d, Errors: %%d' %% (result.testsRun, len(result.failures), len(result.errors)), file=f) >> %TEMP%\econ_tests.py

:: Run the Python script
python %TEMP%\econ_tests.py

:: Check if the output file was created
if exist "%OUTPUT_FILE%" (
    echo.
    echo Test execution complete.
    echo Output saved to: %OUTPUT_FILE%
    
    :: Show first 20 lines of output
    echo.
    echo === FIRST 20 LINES OF OUTPUT ===
    type "%OUTPUT_FILE%" 2>nul | findstr /n "^" | findstr /b "[0-9][0-9]*:" | findstr /b "[0-9]:"
    
    :: Open the output file
    start notepad "%OUTPUT_FILE%"
) else (
    echo.
    echo ERROR: Output file was not created. Check Python errors above.
)

:: Clean up
del %TEMP%\econ_tests.py 2>nul
