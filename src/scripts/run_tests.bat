@echo off
set PYTHONPATH=%~dp0;%PYTHONPATH%
python -c "import sys; print('Python version:', sys.version)"
python -c "import pytest; print('pytest version:', pytest.__version__)"

echo Running tests...
python -m pytest tests/ -v -s

if %ERRORLEVEL% EQU 0 (
    echo All tests passed!
) else (
    echo Some tests failed.
)

pause
