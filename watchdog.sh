#!/bin/bash

################################################################################
# System Monitor - Watchdog Script
# Monitors and restarts services if they crash
# Run this in background: ./watchdog.sh &
################################################################################

AGENT_DIR="$HOME/.sysmon/agent"
NGROK_TOKEN="3DHUSD9zUxwpnhKjhIlfohEJwGk_2UbPU4mcMNW2ZvrMK3oRx"
LOG_FILE="/tmp/sysmon_watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Watchdog Started ==="

while true; do
    # Check Agent
    if ! pgrep -f "rat_agent/agent.py" > /dev/null; then
        log "⚠️  Agent not running - restarting..."
        cd "$AGENT_DIR" && nohup python3 rat_agent/agent.py >> /tmp/sysmon_agent.log 2>&1 &
        log "✅ Agent restarted"
    fi
    
    # Check Dashboard
    if ! pgrep -f "dashboard/app.py" > /dev/null; then
        log "⚠️  Dashboard not running - restarting..."
        cd "$AGENT_DIR" && nohup python3 dashboard/app.py >> /tmp/sysmon_dashboard.log 2>&1 &
        log "✅ Dashboard restarted"
    fi
    
    # Check Ngrok
    if ! pgrep -f "ngrok" > /dev/null; then
        log "⚠️  Ngrok not running - restarting..."
        ngrok http 5000 --authtoken=$NGROK_TOKEN &
        log "✅ Ngrok restarted"
    fi
    
    # Sleep for 30 seconds before next check
    sleep 30
done
