@echo off
setlocal

:: Set Python path to include the project root
set PYTHONPATH=%~dp0;%PYTHONPATH%

:: Run the test runner
python -m pytest src/tests/ -v --log-cli-level=INFO --log-file=tests/results/test_results.log

endlocal
