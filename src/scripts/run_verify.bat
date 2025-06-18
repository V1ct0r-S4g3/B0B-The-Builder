@echo off
setlocal

echo Running verification script...
python verify_python.py > verification_output.txt 2>&1
type verification_output.txt

echo.
echo Running simple test...
python -m pytest tests/test_file_ops.py -v -s > test_output.txt 2>&1
type test_output.txt

echo.
echo Verification complete. Check the output files for details.
