@echo off
echo Running EconomyManager tests...
python -m pytest tests/test_economy_manager.py -v -s > economy_test_output.txt 2>&1
type economy_test_output.txt
echo.
python -m pytest tests/test_economy_manager_extended.py -v -s > economy_extended_test_output.txt 2>&1
type economy_extended_test_output.txt
echo.
echo Test complete. Output saved to economy_test_output.txt and economy_extended_test_output.txt
