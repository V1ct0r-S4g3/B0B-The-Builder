@echo off
:: Get the full path to the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%run_bot.py"

echo Running with administrator privileges...
powershell -Command "Start-Process python -Verb RunAs -ArgumentList '"%SCRIPT_PATH%"' -WorkingDirectory "%SCRIPT_DIR%""

pause
