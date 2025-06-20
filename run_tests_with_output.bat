@echo off
REM Batch file to run tests and capture output

echo Running tests with output capture...
echo =======================================

set TIMESTAMP=%DATE:/=-%_%TIME::=-%
set TIMESTAMP=%TIMESTAMP: =0%
set OUTPUT_FILE=test_output_%TIMESTAMP%.txt

echo Test started at: %DATE% %TIME% > %OUTPUT_FILE%
echo Python Executable: %PYTHON% >> %OUTPUT_FILE%
echo ======================================= >> %OUTPUT_FILE%

REM Test 1: Simple Python version
echo. >> %OUTPUT_FILE%
echo === TEST 1: python --version === >> %OUTPUT_FILE%
python --version 2>> %OUTPUT_FILE%

REM Test 2: Run test_flush.py with python
echo. >> %OUTPUT_FILE%
echo === TEST 2: python test_flush.py === >> %OUTPUT_FILE%
python test_flush.py >> %OUTPUT_FILE% 2>&1

REM Test 3: Run test_flush.py with python -u
echo. >> %OUTPUT_FILE%
echo === TEST 3: python -u test_flush.py === >> %OUTPUT_FILE%
python -u test_flush.py >> %OUTPUT_FILE% 2>&1

REM Test 4: Run with py launcher
echo. >> %OUTPUT_FILE%
echo === TEST 4: py test_flush.py === >> %OUTPUT_FILE%
py test_flush.py >> %OUTPUT_FILE% 2>&1

REM Test 5: Run with specific Python version (3.7+)
echo. >> %OUTPUT_FILE%
echo === TEST 5: py -3 test_flush.py === >> %OUTPUT_FILE%
py -3 test_flush.py >> %OUTPUT_FILE% 2>&1

REM Test 6: Run with pythonw
echo. >> %OUTPUT_FILE%
echo === TEST 6: pythonw test_flush.py === >> %OUTPUT_FILE%
pythonw test_flush.py >> %OUTPUT_FILE% 2>&1

echo. >> %OUTPUT_FILE%
echo ======================================= >> %OUTPUT_FILE%
echo Test completed at: %DATE% %TIME% >> %OUTPUT_FILE%

echo.
echo Test output has been saved to: %OUTPUT_FILE%
start notepad %OUTPUT_FILE%
