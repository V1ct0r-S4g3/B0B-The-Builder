@echo off
echo Starting StarCraft II client...
start "" /B python start_sc2.py

echo Waiting for SC2 to start...
timeout /t 10 /nobreak >nul

echo Starting bot...
python simple_bot.py

pause
