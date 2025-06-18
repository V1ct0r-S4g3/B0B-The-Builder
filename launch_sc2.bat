@echo off
setlocal

set SC2PATH=D:\Battle.net\StarCraft2\Versions\Base94137
set LOGFILE=sc2_launch_%DATE:/=%-%TIME::=%.log
echo Starting SC2 at %TIME% > "%LOGFILE%"

echo SC2 Path: %SC2PATH% >> "%LOGFILE%"
echo Current Directory: %CD% >> "%LOGFILE%"

cd /d "%SC2PATH%"
echo Changed to directory: %CD% >> "%LOGFILE%"

echo Launching SC2 with command: "SC2_x64.exe" -listen 127.0.0.1 -port 8167 -displayMode 0 -windowwidth 1024 -windowheight 768 -noaudio -verbose -temporarybasedir "%TEMP%" -tempDir "%TEMP%" -dataDir "%SC2PATH%" -dataVersion "B89B5D6F-FF17-4DB5-9D97-1281691B3FB4" -eglpath "libEGL.dll" -osmesapath "osmesa.dll" -preload -preload_path "%SC2PATH%" -preload_os -preload_os_path "%SC2PATH%" -preload_os_win -preload_os_win_path "%SC2PATH%" -preload_os_mac -preload_os_mac_path "%SC2PATH%" -preload_os_linux -preload_os_linux_path "%SC2PATH%" -preload_os_linux64 -preload_os_linux64_path "%SC2PATH%" -preload_os_win32 -preload_os_win32_path "%SC2PATH%" -preload_os_win64 -preload_os_win64_path "%SC2PATH%" -preload_os_win64 -preload_os_win64_path "%SC2PATH%" >> "%LOGFILE%"

start "" /B /WAIT "SC2_x64.exe" -listen 127.0.0.1 -port 8167 -displayMode 0 -windowwidth 1024 -windowheight 768 -noaudio -verbose -temporarybasedir "%TEMP%" -tempDir "%TEMP%" -dataDir "%SC2PATH%" -dataVersion "B89B5D6F-FF17-4DB5-9D97-1281691B3FB4" -eglpath "libEGL.dll" -osmesapath "osmesa.dll" -preload -preload_path "%SC2PATH%" -preload_os -preload_os_path "%SC2PATH%" -preload_os_win -preload_os_win_path "%SC2PATH%" -preload_os_mac -preload_os_mac_path "%SC2PATH%" -preload_os_linux -preload_os_linux_path "%SC2PATH%" -preload_os_linux64 -preload_os_linux64_path "%SC2PATH%" -preload_os_win32 -preload_os_win32_path "%SC2PATH%" -preload_os_win64 -preload_os_win64_path "%SC2PATH%" -preload_os_win64 -preload_os_win64_path "%SC2PATH%"

echo SC2 process exited with code %ERRORLEVEL% >> "%LOGFILE%"

tasklist /FI "IMAGENAME eq SC2_x64.exe" | find "SC2_x64.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo SC2 process is running >> "%LOGFILE%"
    echo SC2 process is running
    exit /b 0
) else (
    echo SC2 process failed to start or crashed >> "%LOGFILE%"
    echo SC2 process failed to start or crashed
    exit /b 1
)
