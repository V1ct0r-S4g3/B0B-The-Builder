@echo off
set PYTHONPATH=%~dp0;%PYTHONPATH%
echo Running simple test...
python -c "print('Direct Python print')" > output.txt 2>&1
type output.txt

echo.
echo Running pytest...
python -m pytest tests/test_hello.py -v -s > pytest_output.txt 2>&1
type pytest_output.txt

echo.
echo Test files created:
dir /b output.txt pytest_output.txt
