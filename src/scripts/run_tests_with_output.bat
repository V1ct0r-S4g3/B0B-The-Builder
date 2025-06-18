@echo off
setlocal enabledelayedexpansion

set "TIMESTAMP=%DATE:/=-%_%TIME::=-%"
set "TIMESTAMP=!TIMESTAMP: =0!"
set "OUTPUT_FILE=test_output_!TIMESTAMP!.txt"

echo Running tests and saving output to !OUTPUT_FILE!
echo ===========================================

set PYTHONPATH=%~dp0;%PYTHONPATH%

echo [%TIME%] Running hello test...
python -m pytest tests/test_hello.py -v -s > "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo [%TIME%] Running MilitaryManager simple test...
python -m pytest tests/test_military_simple.py -v -s >> "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo [%TIME%] Running extended MilitaryManager tests...
python -m pytest tests/test_military_manager_extended.py -v -s >> "!OUTPUT_FILE!" 2>&1
type "!OUTPUT_FILE!"

echo.
echo ===========================================
echo Test output has been saved to: "!OUTPUT_FILE!"
pause
