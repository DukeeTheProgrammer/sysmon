@echo off
REM ================================================================================
REM System Monitor - Windows Quick Start
REM ================================================================================

echo Starting System Monitor...

REM Kill existing processes
taskkill /F /IM python.exe 2>nul

REM Start agent
start /B python "%~dp0rat_agent\agent.py"
echo [OK] Agent started

REM Wait
timeout /t 3 /nobreak >nul

REM Start dashboard
start /B python "%~dp0dashboard\app.py"
echo [OK] Dashboard started

echo.
echo System Monitor is running!
echo URL: http://localhost:5000
echo.
pause
