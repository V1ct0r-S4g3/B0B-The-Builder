@echo off
:: Batch file to test SC2 with different compatibility modes

set "SC2_PATH=D:\Battle.net\StarCraft2\Versions\Base94137\SC2_x64.exe"
set "TEMP_DIR=%USERPROFILE%\Documents\StarCraftII"

if not exist "%SC2_PATH%" (
    echo Error: SC2 executable not found at %SC2_PATH%
    pause
    exit /b 1
)

if not exist "%TEMP_DIR%" (
    mkdir "%TEMP_DIR%"
)

echo Testing different compatibility modes...
echo.

echo [1] Windows 8
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /t REG_SZ /d "~ WIN8RTM" /f
call :LaunchAndWait "Windows 8"
if %ERRORLEVEL% == 0 (
    echo Success! SC2 launched successfully with Windows 8 compatibility.
    pause
    exit /b 0
)

echo [2] Windows 7
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /t REG_SZ /d "~ WIN7RTM" /f
call :LaunchAndWait "Windows 7"
if %ERRORLEVEL% == 0 (
    echo Success! SC2 launched successfully with Windows 7 compatibility.
    pause
    exit /b 0
)

echo [3] Windows 8.1
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /t REG_SZ /d "~ WIN81RTM" /f
call :LaunchAndWait "Windows 8.1"
if %ERRORLEVEL% == 0 (
    echo Success! SC2 launched successfully with Windows 8.1 compatibility.
    pause
    exit /b 0
)

echo [4] Windows 10
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /t REG_SZ /d "~ WIN10RTM" /f
call :LaunchAndWait "Windows 10"
if %ERRORLEVEL% == 0 (
    echo Success! SC2 launched successfully with Windows 10 compatibility.
    pause
    exit /b 0
)

echo [5] Basic settings (no compatibility mode)
reg delete "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "%SC2_PATH%" /f
start "" "%SC2_PATH%" -listen 127.0.0.1 -port 8167 -displayMode 0 -windowwidth 1024 -windowheight 768 -noaudio -verbose -tempDir "%TEMP_DIR%"

echo.
echo All compatibility modes tested. If SC2 didn't launch, please check for other issues.
pause
exit /b 0

:LaunchAndWait
echo Testing with %1 compatibility...
start "" "%SC2_PATH%" -listen 127.0.0.1 -port 8167 -displayMode 0 -windowwidth 1024 -windowheight 768 -noaudio -verbose -tempDir "%TEMP_DIR%"

echo Waiting 10 seconds to see if SC2 stays running...
timeout /t 10 /nobreak >nul

tasklist /FI "IMAGENAME eq SC2_x64.exe" 2>nul | find /I "SC2_x64.exe" >nul
if %ERRORLEVEL% == 0 (
    echo SC2 is still running with %1 compatibility.
    exit /b 0
) else (
    echo SC2 crashed or didn't start with %1 compatibility.
    exit /b 1
)
