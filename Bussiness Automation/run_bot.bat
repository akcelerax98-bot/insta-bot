@echo off
title Instagram Bot - Running 24/7
color 0A

:start
echo ============================================
echo   Instagram Automation Bot Starting...
echo ============================================
echo.

cd /d "C:\Users\kames\OneDrive\Documents\Bussiness Automation"

echo Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo Bot is now running. Do NOT close this window.
echo Logs are saved to bot.log
echo.

python main.py

echo.
echo ============================================
echo  Bot stopped or crashed. Restarting in 30s...
echo ============================================
timeout /t 30
goto start
