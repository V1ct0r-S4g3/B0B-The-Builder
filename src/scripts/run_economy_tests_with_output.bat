@echo off
setlocal enabledelayedexpansion

set "TIMESTAMP=%DATE:/=-%_%TIME::=-%"
set "TIMESTAMP=!TIMESTAMP: =0!"
set "OUTPUT_FILE=economy_test_output_!TIMESTAMP!.txt"

echo Running EconomyManager tests and saving output to !OUTPUT_FILE!
echo =======================================================

set PYTHONPATH=%~dp0;%PYTHONPATH%

echo [%TIME%] Running direct EconomyManager tests...
python -m unittest tests/test_economy_direct.py -v > "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo [%TIME%] Running pytest EconomyManager tests...
python -m pytest tests/test_economy_manager.py -v >> "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo [%TIME%] Running extended EconomyManager tests...
python -m pytest tests/test_economy_manager_extended.py -v >> "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo [%TIME%] All EconomyManager tests completed.
echo Output saved to: !OUTPUT_FILE!
