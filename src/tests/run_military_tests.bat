@echo off
echo Running MilitaryManager tests...

:: Change to the src directory where pytest.ini is located
cd /d %~dp0..

:: Run the tests with coverage
python -m pytest tests/test_military_manager.py ^
    -v ^
    --cov=src.managers.military ^
    --cov-report=term-missing ^
    > tests/test_outputs/military_test_output.txt 2>&1

echo.
echo Test output saved to tests/test_outputs/military_test_output.txt
