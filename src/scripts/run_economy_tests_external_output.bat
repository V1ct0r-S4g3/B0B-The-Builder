@echo off
setlocal enabledelayedexpansion

:: Create output directory if it doesn't exist
if not exist "%USERPROFILE%\\Documents\\SC2BotTests" mkdir "%USERPROFILE%\\Documents\\SC2BotTests"

:: Create timestamp for filename
set "TIMESTAMP=%DATE:/=-%_%TIME::=-%"
set "TIMESTAMP=!TIMESTAMP: =0!"
set "OUTPUT_FILE=%USERPROFILE%\\Documents\\SC2BotTests\\economy_tests_!TIMESTAMP!.txt"

echo Running EconomyManager tests...
echo Output will be saved to: %OUTPUT_FILE%
echo =======================================================

:: Set Python path
set PYTHONPATH=%~dp0;%PYTHONPATH%

:: Run tests with output to file
echo [%TIME%] Running direct EconomyManager tests... > "%OUTPUT_FILE%"
python -m unittest tests/test_economy_direct.py -v >> "%OUTPUT_FILE%" 2>&1

echo [%TIME%] Running pytest EconomyManager tests... >> "%OUTPUT_FILE%"
python -m pytest tests/test_economy_manager.py -v >> "%OUTPUT_FILE%" 2>&1

echo [%TIME%] Running extended EconomyManager tests... >> "%OUTPUT_FILE%"
python -m pytest tests/test_economy_manager_extended.py -v >> "%OUTPUT_FILE%" 2>&1

echo [%TIME%] All EconomyManager tests completed. >> "%OUTPUT_FILE%"

echo.
echo Test execution complete.
echo Results saved to: %OUTPUT_FILE%

:: Open the output file in notepad
notepad "%OUTPUT_FILE%"
