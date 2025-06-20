@echo off
:: Batch file to run the bot as administrator

:: Get the directory this batch file is in
set "SCRIPT_DIR=%~dp0"

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
    echo Changing to directory: %SCRIPT_DIR%
    cd /d "%SCRIPT_DIR%"
    python run_bot.py
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c cd /d """%SCRIPT_DIR%""" && """%~f0"""'"
    exit /b
)

pause
