# Wayland Screen Capture Fix

## The Issue

On **Wayland** (default on newer Fedora/Ubuntu), screen capture shows **black screen** because:
- Wayland has stricter security than X11
- Apps need permission to capture the screen
- `mss` and `pyautogui` have limited Wayland support

**Mouse control works fine** - only screen capture is affected.

## Solutions

### Option 1: Install scrot (Recommended for Linux)

```bash
# Fedora/RHEL
sudo dnf install scrot

# Ubuntu/Debian
sudo apt install scrot

# Arch
sudo pacman -S scrot
```

Then restart the dashboard:
```bash
cd /home/dukeetheprogrammer/rat && ./install.sh
```

### Option 2: Switch to X11 (Easiest)

**On next login:**
1. At login screen, click gear/settings icon
2. Select "GNOME on Xorg" or "Ubuntu on Xorg"
3. Login normally

Or logout and choose X11 session.

### Option 3: Use grim (For Wayland)

```bash
# Install grim
sudo dnf install grim  # Fedora
sudo apt install grim  # Ubuntu

# The agent will automatically use it
```

### Option 4: Enable X11 Forwarding for pyautogui

```bash
# Add to ~/.bashrc or ~/.profile
export QT_QPA_PLATFORM=xcb

# Then restart terminal and run agent
```

## Quick Test

Test if capture works:

```bash
cd /home/dukeetheprogrammer/rat
python3 -c "
from rat_agent.screen import RemoteScreen
from PIL import Image
import io

s = RemoteScreen()
img_data = s._capture_screen()

if img_data:
    img = Image.open(io.BytesIO(img_data))
    pixels = list(img.getdata())
    black = sum(1 for p in pixels if p[0] < 10 and p[1] < 10 and p[2] < 10)
    pct = (black / len(pixels)) * 100
    print(f'Black pixels: {pct:.1f}%')
    if pct < 50:
        print('✅ Working!')
    else:
        print('⚠️ Still black - try solutions above')
"
```

## Status by Platform

| Platform | Screen Capture | Mouse Control |
|----------|---------------|---------------|
| **Windows** | ✅ Works | ✅ Works |
| **Linux (X11)** | ✅ Works | ✅ Works |
| **Linux (Wayland)** | ⚠️ Needs scrot/grim | ✅ Works |
| **macOS** | ✅ Works | ⚠️ Limited |

## Current Status

- ✅ **Mouse control**: Working on Wayland
- ⚠️ **Screen capture**: Black on Wayland (needs scrot/grim or switch to X11)

## For Users

If you see black screen:

1. **Try installing scrot:**
   ```bash
   sudo dnf install scrot  # or apt/pacman
   ```

2. **Restart dashboard:**
   ```bash
   cd /home/dukeetheprogrammer/rat && ./install.sh
   ```

3. **Or switch to X11** at login screen

4. **Mouse control still works** even if screen is black!

## For Development

The agent now tries capture methods in this order:
1. pyautogui (Windows/Linux/macOS)
2. ImageMagick import (Linux X11)
3. mss (Linux X11)
4. scrot (Linux)

It automatically detects and uses the best available method.
