#!/bin/bash

################################################################################
# System Monitor - Quick Start Script
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting System Monitor..."

# Kill existing processes
pkill -f "python3.*rat_agent/agent.py" 2>/dev/null || true
pkill -f "python3.*dashboard/app.py" 2>/dev/null || true
pkill -f "ngrok http" 2>/dev/null || true
sleep 2

# Start agent
nohup python3 "$SCRIPT_DIR/rat_agent/agent.py" > /tmp/opencode/sysmon_agent.log 2>&1 &
echo "Agent started"

# Start dashboard
nohup python3 "$SCRIPT_DIR/dashboard/app.py" > /tmp/opencode/sysmon_dashboard.log 2>&1 &
echo "Dashboard started"

# Wait for dashboard
sleep 5

# Start ngrok
nohup ~/.local/bin/ngrok http 5000 > /tmp/opencode/ngrok.log 2>&1 &
echo "Ngrok started"

# Wait and get URL
sleep 5
PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null || echo "")

echo ""
echo "========================================"
echo "System Monitor is Running"
echo "========================================"
echo ""
echo "Public URL: $PUBLIC_URL"
echo "Local URL:  http://localhost:5000"
echo ""
echo "Login: admin / rat_admin_2024"
echo ""
echo "Log Files:"
echo "  Agent:     /tmp/opencode/sysmon_agent.log"
echo "  Dashboard: /tmp/opencode/sysmon_dashboard.log"
echo "  Ngrok:     /tmp/opencode/ngrok.log"
echo ""
echo "To stop: pkill -f 'python3.*(agent|app)' && pkill -f ngrok"
