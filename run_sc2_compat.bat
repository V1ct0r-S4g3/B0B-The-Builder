@echo off
:: Batch file to run SC2 with compatibility settings

set "SC2_PATH=D:\Battle.net\StarCraft2\Versions\Base94137\SC2_x64.exe"
set "TEMP_DIR=%USERPROFILE%\Documents\StarCraftII"

if not exist "%SC2_PATH%" (
    echo Error: SC2 executable not found at %SC2_PATH%
    pause
    exit /b 1
)

echo Creating compatibility settings for SC2...
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /t REG_SZ /d "~ WIN8RTM DISABLEDWM HIGHDPIAWARE" /f

if not exist "%TEMP_DIR%" (
    mkdir "%TEMP_DIR%"
)

echo Launching StarCraft II with compatibility settings...
start "" "%SC2_PATH%" -listen 127.0.0.1 -port 8167 -displayMode 0 -windowwidth 1024 -windowheight 768 -noaudio -verbose -tempDir "%TEMP_DIR%"

echo.
echo If SC2 launches successfully, try running the bot again.
pause
