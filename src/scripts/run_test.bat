@echo off
echo Running tests...
python -m pytest tests/test_basic.py -v -s > test_output.txt 2>&1
type test_output.txt
echo.
echo Test complete. Output saved to test_output.txt
