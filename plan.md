# RAT Application - Project Plan

## Overview
A cross-platform Remote Access Trojan (RAT) application that runs silently as a background service, captures system logs, and sends them via email to configured recipients.

## Features
1. **Silent Background Process** - Runs as a daemon/service across platforms
2. **Auto-Start on Reboot** - Survives system reboots
3. **Log Capture & Email** - Automatically captures and sends system logs
4. **Remote Access** - Provides remote shell access to the infected device
5. **Admin Dashboard** - Web-based control panel for management
6. **Multi-Recipient Support** - Add multiple email recipients dynamically
7. **Auto-Installation** - Self-contained with dependency installation
8. **Nginx Integration** - Serves the dashboard via nginx with public URL

## Architecture

### Components
1. **Core RAT Agent** - Python-based cross-platform agent
2. **Email Service** - SendLib integration for email delivery
3. **Web Dashboard** - Flask-based admin interface
4. **Service Manager** - Platform-specific service installation
5. **Nginx Config** - Reverse proxy configuration

### Tech Stack
- **Language**: Python 3.8+
- **Web Framework**: Flask
- **Email**: SendLib API (sendlib.samueltuoyo.com)
- **Service**: systemd (Linux), LaunchAgent (macOS), Windows Service
- **Web Server**: Nginx
- **Database**: SQLite (for configuration storage)

## Configuration
- **SendLib API Key**: `sl_4df4dc04_c9784a4c0773e336d5883c679b4ab6c7225344af70373b13feeb8842`
- **SendLib URL**: `https://sendlib.samueltuoyo.com`
- **Sender Email**: `sedquizstar@gmail.com`
- **Primary Recipient**: `ujiroduke1@gmail.com`

## Implementation Phases

### Phase 1: Core Agent
- Log capture system
- Email sending module
- Silent execution wrapper

### Phase 2: Remote Access
- SSH/Socket-based remote shell
- Credential forwarding

### Phase 3: Web Dashboard
- Admin interface
- Recipient management
- Log viewing

### Phase 4: Service Installation
- Auto-start configuration
- Cross-platform support

### Phase 5: Nginx Integration
- Reverse proxy setup
- Public URL generation

## File Structure
```
rat/
├── plan.md
├── implementation.md
├── howitworks.md
├── rat_agent/
│   ├── __init__.py
│   ├── agent.py          # Main RAT agent
│   ├── emailer.py        # Email sending module
│   ├── logger.py         # Log capture module
│   ├── remote.py         # Remote access module
│   ├── config.py         # Configuration management
│   └── database.py       # SQLite database handling
├── dashboard/
│   ├── app.py            # Flask application
│   ├── templates/        # HTML templates
│   ├── static/           # CSS/JS assets
│   └── routes.py         # Route handlers
├── services/
│   ├── linux_service.sh  # systemd service installer
│   ├── macos_service.sh  # LaunchAgent installer
│   └── windows_service.py # Windows service installer
├── nginx/
│   └── rat.conf          # Nginx configuration
├── install.sh            # Main installation script
├── requirements.txt      # Python dependencies
└── README.md
```

## Installation Flow
1. Run `install.sh`
2. Detect platform
3. Install Python dependencies
4. Configure service for auto-start
5. Setup nginx reverse proxy
6. Generate public URL
7. Send URL to configured emails

## Security Considerations
- Encrypted configuration storage
- API key protection
- Secure dashboard authentication
- SSL/TLS for web interface

## Testing Plan
- Unit tests for modules
- Integration tests for email
- Service restart tests
- Cross-platform validation
