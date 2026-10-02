# Remote Screen Control - Quick Start

## What's New

### 🖥️ Full-Screen Live View
- **Fullscreen button** for immersive viewing
- Screen takes up entire viewport
- Controls float on side (desktop) or bottom (mobile)

### 📱 Touch/Mouse Control
- **Tap anywhere** to click at that position
- **Drag to move** mouse cursor
- Visual touch indicators show click positions
- Right-click support via context menu or button

### 🚀 Auto-Install Tools
- Automatically detects system type (Debian, RHEL, Arch)
- Installs `xdotool` and `ImageMagick` if missing
- Fallback mechanisms if tools not available

### ⚡ Real-Time Feed
- ~3 FPS smooth streaming
- JPEG compression for bandwidth efficiency
- Mouse position tracking

## One-Step Install

```bash
cd /home/dukeetheprogrammer/rat
./install.sh
```

That's it! Everything starts automatically.

## Access

**URL:** https://unmade-backboned-agreeably.ngrok-free.dev  
**Login:** admin / rat_admin_2024

## How to Use

### 1. Navigate
Click **"Remote Screen"** in sidebar

### 2. Start
Click **"Start Capture"** button

### 3. Control

**On Desktop:**
- Click on screen → left-clicks there
- Right-click on screen → right-clicks there
- Drag → moves mouse
- Use control panel for specific actions

**On Mobile:**
- Tap → clicks at tap position
- Drag → moves mouse around
- Fullscreen → better viewing

### 4. Type Text
1. Enter text in "Type Text" box
2. Click "Send"
3. Text types on remote system

### 5. Fullscreen
Click **"Fullscreen"** button for:
- Larger view
- Better mobile experience
- Immersive control

## Manual Tool Install (if needed)

```bash
# Debian/Ubuntu
sudo apt-get install xdotool imagemagick

# RHEL/Fedora
sudo dnf install xdotool ImageMagick

# Or use helper script
cd /home/dukeetheprogrammer/rat
./install_tools.sh
```

## Features

| Feature | Status |
|---------|--------|
| Live screen feed | ✅ |
| Mouse movement | ✅ |
| Click (left/right) | ✅ |
| Double-click | ✅ |
| Type text | ✅ |
| Fullscreen mode | ✅ |
| Touch controls | ✅ |
| Mobile optimized | ✅ |
| Auto tool install | ✅ |
| Multi-monitor support | ✅ |

## Troubleshooting

**Screen is black:**
- Need display server running
- Run: `startx` or check display

**Mouse doesn't move:**
- Install xdotool: `sudo apt-get install xdotool`
- Restart dashboard

**Slow updates:**
- Check network connection
- Reduce quality in screen.py

## Files Changed

- `rat_agent/screen.py` - Auto-install, better controls
- `dashboard/templates/index.html` - Fullscreen, touch UI
- `dashboard/app.py` - WebSocket handlers
- `install.sh` - Tool installation
- `install_tools.sh` - Helper script

## Auto-Start

Everything auto-starts on reboot via cron:
```bash
@reboot cd /home/dukeetheprogrammer/rat && ...
```

No manual intervention needed!
