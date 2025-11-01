import os
import shutil
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Set, Tuple, Optional
import threading
import time
import sys

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Tip: Cài đặt 'tqdm' để có progress bar đẹp hơn: pip install tqdm")

# Detect if running on Windows
if os.name == 'nt':
    try:
        import msvcrt
        ARROW_KEYS_AVAILABLE = True
    except ImportError:
        ARROW_KEYS_AVAILABLE = False
else:
    try:
        import termios
        import tty
        ARROW_KEYS_AVAILABLE = True
    except ImportError:
        ARROW_KEYS_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# THEMES - Catppuccin & More
# ═══════════════════════════════════════════════════════════════
class Theme:
    """Base theme class"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class CatppuccinMocha(Theme):
    """Catppuccin Mocha - Dark, warm theme"""
    BLUE = '\033[38;5;117m'      # Lavender
    CYAN = '\033[38;5;159m'      # Sky
    GREEN = '\033[38;5;115m'     # Green
    YELLOW = '\033[38;5;222m'    # Yellow
    RED = '\033[38;5;210m'       # Red
    MAGENTA = '\033[38;5;183m'   # Mauve
    ORANGE = '\033[38;5;216m'    # Peach
    BORDER = '\033[38;5;240m'
    TEXT = '\033[38;5;250m'
    ACCENT = '\033[38;5;183m'

class CatppuccinLatte(Theme):
    """Catppuccin Latte - Light, warm theme"""
    BLUE = '\033[38;5;32m'       # Blue
    CYAN = '\033[38;5;37m'       # Sky
    GREEN = '\033[38;5;64m'      # Green
    YELLOW = '\033[38;5;136m'    # Yellow
    RED = '\033[38;5;167m'       # Red
    MAGENTA = '\033[38;5;133m'   # Mauve
    ORANGE = '\033[38;5;166m'    # Peach
    BORDER = '\033[38;5;245m'
    TEXT = '\033[38;5;240m'
    ACCENT = '\033[38;5;133m'

class CatppuccinFrappe(Theme):
    """Catppuccin Frappé - Cool, dark theme"""
    BLUE = '\033[38;5;111m'      # Lavender
    CYAN = '\033[38;5;153m'      # Sky
    GREEN = '\033[38;5;108m'     # Green
    YELLOW = '\033[38;5;229m'    # Yellow
    RED = '\033[38;5;204m'       # Red
    MAGENTA = '\033[38;5;182m'   # Mauve
    ORANGE = '\033[38;5;215m'    # Peach
    BORDER = '\033[38;5;238m'
    TEXT = '\033[38;5;248m'
    ACCENT = '\033[38;5;182m'

class CatppuccinMacchiato(Theme):
    """Catppuccin Macchiato - Warm, medium theme"""
    BLUE = '\033[38;5;110m'      # Lavender
    CYAN = '\033[38;5;159m'      # Sky
    GREEN = '\033[38;5;108m'     # Green
    YELLOW = '\033[38;5;222m'    # Yellow
    RED = '\033[38;5;204m'       # Red
    MAGENTA = '\033[38;5;183m'   # Mauve
    ORANGE = '\033[38;5;216m'    # Peach
    BORDER = '\033[38;5;239m'
    TEXT = '\033[38;5;249m'
    ACCENT = '\033[38;5;183m'

class TokyoNight(Theme):
    """Tokyo Night - Dark blue theme"""
    BLUE = '\033[38;5;75m'       # Bright blue
    CYAN = '\033[38;5;87m'       # Cyan
    GREEN = '\033[38;5;114m'     # Green
    YELLOW = '\033[38;5;228m'    # Yellow
    RED = '\033[38;5;204m'       # Red
    MAGENTA = '\033[38;5;213m'   # Purple
    ORANGE = '\033[38;5;215m'    # Orange
    BORDER = '\033[38;5;238m'
    TEXT = '\033[38;5;252m'
    ACCENT = '\033[38;5;213m'

class Dracula(Theme):
    """Dracula - Purple dark theme"""
    BLUE = '\033[38;5;117m'      # Cyan
    CYAN = '\033[38;5;159m'      # Light cyan
    GREEN = '\033[38;5;84m'      # Green
    YELLOW = '\033[38;5;228m'    # Yellow
    RED = '\033[38;5;212m'       # Pink
    MAGENTA = '\033[38;5;141m'   # Purple
    ORANGE = '\033[38;5;215m'    # Orange
    BORDER = '\033[38;5;236m'
    TEXT = '\033[38;5;253m'
    ACCENT = '\033[38;5;141m'

class Nord(Theme):
    """Nord - Cool, minimal theme"""
    BLUE = '\033[38;5;110m'      # Frost blue
    CYAN = '\033[38;5;117m'      # Light blue
    GREEN = '\033[38;5;108m'     # Aurora green
    YELLOW = '\033[38;5;223m'    # Aurora yellow
    RED = '\033[38;5;203m'       # Aurora red
    MAGENTA = '\033[38;5;139m'   # Aurora purple
    ORANGE = '\033[38;5;216m'    # Aurora orange
    BORDER = '\033[38;5;237m'
    TEXT = '\033[38;5;250m'
    ACCENT = '\033[38;5;110m'

class Gruvbox(Theme):
    """Gruvbox - Retro, warm theme"""
    BLUE = '\033[38;5;109m'      # Blue
    CYAN = '\033[38;5;108m'      # Aqua
    GREEN = '\033[38;5;142m'     # Green
    YELLOW = '\033[38;5;214m'    # Yellow
    RED = '\033[38;5;167m'       # Red
    MAGENTA = '\033[38;5;175m'   # Purple
    ORANGE = '\033[38;5;208m'    # Orange
    BORDER = '\033[38;5;239m'
    TEXT = '\033[38;5;223m'
    ACCENT = '\033[38;5;142m'

# Available themes
THEMES = {
    'mocha': CatppuccinMocha,
    'latte': CatppuccinLatte,
    'frappe': CatppuccinFrappe,
    'macchiato': CatppuccinMacchiato,
    'tokyo': TokyoNight,
    'dracula': Dracula,
    'nord': Nord,
    'gruvbox': Gruvbox
}

# ═══════════════════════════════════════════════════════════════
# LANGUAGES
# ═══════════════════════════════════════════════════════════════
LANGUAGES = {
    'vi': {
        'title': 'CÔNG CỤ ĐỒNG BỘ FILE NÂNG CAO',
        'subtitle': 'Hyprland Edition',
        'select_drive': 'CHỌN Ổ ĐĨA',
        'select_action': 'CHỌN THAO TÁC',
        'source': 'Chọn ổ đĩa nguồn (Source)',
        'destination': 'Chọn ổ đĩa đích (Destination)',
        'custom_path': 'Nhập đường dẫn tùy chỉnh',
        'selected_source': 'Đã chọn nguồn:',
        'selected_dest': 'Đã chọn đích:',
        'menu_compare': 'So sánh hai ổ đĩa',
        'menu_compare_desc': 'Phân tích sự khác biệt',
        'menu_preview': 'Xem trước (Dry run)',
        'menu_preview_desc': 'Kiểm tra trước khi sync',
        'menu_sync': 'Sync nhanh',
        'menu_sync_desc': 'Copy files song song',
        'menu_secure': 'Sync an toàn',
        'menu_secure_desc': 'Verify bằng hash',
        'menu_clear': 'Xóa trạng thái',
        'menu_clear_desc': 'Clear resume state',
        'menu_reselect': 'Chọn lại ổ đĩa',
        'menu_reselect_desc': 'Đổi nguồn/đích',
        'menu_settings': 'Cài đặt',
        'menu_settings_desc': 'Theme & Language',
        'menu_exit': 'Thoát',
        'menu_exit_desc': 'Exit program',
        'choose_drive': 'Chọn ổ đĩa',
        'choose_action': 'Chọn thao tác',
        'enter_path': 'Nhập đường dẫn',
        'path_not_exist': 'Đường dẫn không tồn tại!',
        'no_drives': 'Không tìm thấy ổ đĩa nào!',
        'invalid_choice': 'Lựa chọn không hợp lệ!',
        'cancelled': 'Đã hủy thao tác',
        'press_enter': 'Nhấn Enter để tiếp tục',
        'loading': 'Đang tải',
        'scanning': 'Đang quét',
        'comparing': 'Đang so sánh files',
        'selecting': 'Đang chọn',
        'starting': 'Đang khởi động',
        'free': 'free',
        'used': 'used',
        'goodbye': 'Tạm biệt!',
        'settings_title': 'CÀI ĐẶT',
        'theme': 'Theme',
        'language': 'Ngôn ngữ',
        'current': 'Hiện tại',
        'select_theme': 'Chọn theme',
        'select_language': 'Chọn ngôn ngữ',
        'apply': 'Áp dụng',
        'back': 'Quay lại',
    },
    'en': {
        'title': 'ADVANCED FILE SYNC TOOL',
        'subtitle': 'Hyprland Edition',
        'select_drive': 'SELECT DRIVE',
        'select_action': 'SELECT ACTION',
        'source': 'Select source drive',
        'destination': 'Select destination drive',
        'custom_path': 'Enter custom path',
        'selected_source': 'Selected source:',
        'selected_dest': 'Selected destination:',
        'menu_compare': 'Compare two drives',
        'menu_compare_desc': 'Analyze differences',
        'menu_preview': 'Preview (Dry run)',
        'menu_preview_desc': 'Check before sync',
        'menu_sync': 'Quick sync',
        'menu_sync_desc': 'Parallel copy',
        'menu_secure': 'Secure sync',
        'menu_secure_desc': 'Verify with hash',
        'menu_clear': 'Clear state',
        'menu_clear_desc': 'Clear resume state',
        'menu_reselect': 'Reselect drives',
        'menu_reselect_desc': 'Change source/dest',
        'menu_settings': 'Settings',
        'menu_settings_desc': 'Theme & Language',
        'menu_exit': 'Exit',
        'menu_exit_desc': 'Exit program',
        'choose_drive': 'Choose drive',
        'choose_action': 'Choose action',
        'enter_path': 'Enter path',
        'path_not_exist': 'Path does not exist!',
        'no_drives': 'No drives found!',
        'invalid_choice': 'Invalid choice!',
        'cancelled': 'Operation cancelled',
        'press_enter': 'Press Enter to continue',
        'loading': 'Loading',
        'scanning': 'Scanning',
        'comparing': 'Comparing files',
        'selecting': 'Selecting',
        'starting': 'Starting',
        'free': 'free',
        'used': 'used',
        'goodbye': 'Goodbye!',
        'settings_title': 'SETTINGS',
        'theme': 'Theme',
        'language': 'Language',
        'current': 'Current',
        'select_theme': 'Select theme',
        'select_language': 'Select language',
        'apply': 'Apply',
        'back': 'Back',
    }
}

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
class Config:
    """Configuration manager"""
    def __init__(self):
        self.config_file = 'file_sync_config.json'
        self.theme = 'mocha'
        self.language = 'vi'
        self.load()
    
    def load(self):
        """Load config from file"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.theme = data.get('theme', 'mocha')
                    self.language = data.get('language', 'vi')
            except:
                pass
    
    def save(self):
        """Save config to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'theme': self.theme,
                    'language': self.language
                }, f, indent=2)
        except:
            pass
    
    def get_theme(self):
        """Get current theme"""
        return THEMES.get(self.theme, CatppuccinMocha)
    
    def get_lang(self):
        """Get current language"""
        return LANGUAGES.get(self.language, LANGUAGES['vi'])

# Global config
config = Config()
Colors = config.get_theme()
lang = config.get_lang()

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text: str):
    """Print styled header"""
    width = 80
    print(f"\n{Colors.BORDER}{'═' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.RESET}")
    print(f"{Colors.BORDER}{'═' * width}{Colors.RESET}\n")

def print_section(text: str):
    """Print section title"""
    print(f"\n{Colors.MAGENTA}╭─{Colors.RESET} {Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")

def print_item(icon: str, text: str, value: str = None, color: str = None):
    """Print list item with icon"""
    if color is None:
        color = Colors.TEXT
    if value:
        print(f"{Colors.MAGENTA}│{Colors.RESET} {icon} {color}{text}{Colors.RESET} {Colors.ACCENT}{value}{Colors.RESET}")
    else:
        print(f"{Colors.MAGENTA}│{Colors.RESET} {icon} {color}{text}{Colors.RESET}")

def print_box(items: list):
    """Print items in a box"""
    print(f"{Colors.BORDER}╭{'─' * 76}╮{Colors.RESET}")
    for item in items:
        print(f"{Colors.BORDER}│{Colors.RESET} {Colors.TEXT}{item:<74}{Colors.BORDER}│{Colors.RESET}")
    print(f"{Colors.BORDER}╰{'─' * 76}╯{Colors.RESET}")

def print_progress(current: int, total: int, prefix: str = ""):
    """Print progress bar"""
    percent = current / total * 100 if total > 0 else 0
    filled = int(50 * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (50 - filled)
    print(f"\r{Colors.MAGENTA}│{Colors.RESET} {prefix} {Colors.CYAN}{bar}{Colors.RESET} {Colors.YELLOW}{percent:.1f}%{Colors.RESET} ({current}/{total})", end='', flush=True)

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}{Colors.BOLD}✓{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}{Colors.BOLD}✗{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}{Colors.BOLD}ℹ{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}")

def animate_loading(text: str, duration: float = 1.0):
    """Animated loading effect"""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Colors.CYAN}{frames[i % len(frames)]}{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}", end='', flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{Colors.GREEN}✓{Colors.RESET} {Colors.TEXT}{text}{Colors.RESET}")

def get_input(prompt: str, color: str = None) -> str:
    """Styled input"""
    if color is None:
        color = Colors.CYAN
    return input(f"{color}{Colors.BOLD}❯{Colors.RESET} {Colors.TEXT}{prompt}{Colors.RESET} ")

def get_key():
    """Get single keypress (cross-platform)"""
    if os.name == 'nt':  # Windows
        if not ARROW_KEYS_AVAILABLE:
            return input()
        
        key = msvcrt.getch()
        if key in [b'\x00', b'\xe0']:  # Arrow key prefix
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                return 'up'
            elif key == b'P':  # Down arrow
                return 'down'
        elif key == b'\r':  # Enter
            return 'enter'
        elif key == b'\x1b':  # ESC
            return 'esc'
        else:
            try:
                return key.decode('utf-8')
            except:
                return ''
    else:  # Unix/Linux/Mac
        if not ARROW_KEYS_AVAILABLE:
            return input()
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
                return 'esc'
            elif ch == '\r' or ch == '\n':
                return 'enter'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def select_with_arrows(items: list, prompt: str = "") -> int:
    """Select item using arrow keys"""
    if not ARROW_KEYS_AVAILABLE:
        # Fallback to number input
        while True:
            try:
                choice = get_input(prompt or "Choose")
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return idx
                print_error(lang['invalid_choice'])
            except ValueError:
                print_error(lang['invalid_choice'])
            except KeyboardInterrupt:
                return -1
    
    selected = 0
    
    while True:
        # Clear and redraw
        print('\033[2J\033[H', end='')  # Clear screen and move to top
        
        # Show banner again if needed
        banner = [
            f"{Colors.CYAN}  ███████╗██╗██╗     ███████╗    ███████╗██╗   ██╗███╗   ██╗ ██████╗{Colors.RESET}",
            f"{Colors.CYAN}  ██╔════╝██║██║     ██╔════╝    ██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝{Colors.RESET}",
            f"{Colors.BLUE}  █████╗  ██║██║     █████╗      ███████╗ ╚████╔╝ ██╔██╗ ██║██║     {Colors.RESET}",
            f"{Colors.BLUE}  ██╔══╝  ██║██║     ██╔══╝      ╚════██║  ╚██╔╝  ██║╚██╗██║██║     {Colors.RESET}",
            f"{Colors.MAGENTA}  ██║     ██║███████╗███████╗    ███████║   ██║   ██║ ╚████║╚██████╗{Colors.RESET}",
            f"{Colors.MAGENTA}  ╚═╝     ╚═╝╚══════╝╚══════╝    ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝{Colors.RESET}",
        ]
        for line in banner:
            print(line)
        
        print_header(prompt)
        
        # Show items with selection
        for i, item in enumerate(items):
            if i == selected:
                # Highlighted item
                print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.GREEN}▶{Colors.RESET} {Colors.BOLD}{Colors.CYAN}{item}{Colors.RESET}")
            else:
                # Normal item
                print(f"{Colors.MAGENTA}│{Colors.RESET}   {Colors.TEXT}{item}{Colors.RESET}")
        
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        print(f"\n{Colors.DIM}Use ↑↓ arrows to navigate, Enter to select, ESC to cancel{Colors.RESET}")
        
        # Get key
        key = get_key()
        
        if key == 'up':
            selected = (selected - 1) % len(items)
        elif key == 'down':
            selected = (selected + 1) % len(items)
        elif key == 'enter':
            return selected
        elif key == 'esc':
            return -1

def refresh_colors():
    """Refresh color scheme after theme change"""
    global Colors
    Colors = config.get_theme()
    # Update CHECK, CROSS, ARROW icons
    Colors.CHECK = f'{Colors.GREEN}✓{Colors.RESET}'
    Colors.CROSS = f'{Colors.RED}✗{Colors.RESET}'
    Colors.ARROW = f'{Colors.CYAN}→{Colors.RESET}'
    Colors.STAR = f'{Colors.YELLOW}★{Colors.RESET}'
    Colors.DOT = f'{Colors.MAGENTA}•{Colors.RESET}'

def show_settings():
    """Show settings menu with arrow navigation"""
    global config, Colors, lang
    
    themes_display = {
        'mocha': ('Catppuccin Mocha', '🌙 Dark, warm'),
        'latte': ('Catppuccin Latte', '☀️  Light, warm'),
        'frappe': ('Catppuccin Frappé', '❄️  Cool, dark'),
        'macchiato': ('Catppuccin Macchiato', '🍂 Warm, medium'),
        'tokyo': ('Tokyo Night', '🌃 Dark blue'),
        'dracula': ('Dracula', '🧛 Purple dark'),
        'nord': ('Nord', '🏔️  Cool, minimal'),
        'gruvbox': ('Gruvbox', '📺 Retro, warm')
    }
    
    languages_display = {
        'vi': ('Tiếng Việt', '🇻🇳'),
        'en': ('English', '🇬🇧')
    }
    
    # Combine all options
    all_options = []
    option_map = []
    
    # Add themes
    for key, (name, desc) in themes_display.items():
        current_mark = '●' if key == config.theme else ' '
        all_options.append(f"{current_mark} {name:<25} {desc}")
        option_map.append(('theme', key))
    
    # Add separator
    all_options.append("─" * 60)
    option_map.append(('separator', None))
    
    # Add languages
    for key, (name, flag) in languages_display.items():
        current_mark = '●' if key == config.language else ' '
        all_options.append(f"{current_mark} {name:<25} {flag}")
        option_map.append(('language', key))
    
    # Add separator
    all_options.append("─" * 60)
    option_map.append(('separator', None))
    
    # Add back option
    all_options.append(f"← {lang['back']}")
    option_map.append(('back', None))
    
    selected = 0
    preview_mode = {}  # Track which themes are in preview mode
    
    while True:
        clear_screen()
        
        # Banner
        print(f"{Colors.CYAN}  ╔═══════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}  ║{Colors.RESET}                     {Colors.BOLD}{Colors.MAGENTA}⚙  SETTINGS  ⚙{Colors.RESET}                     {Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}  ╚═══════════════════════════════════════════════════════════╝{Colors.RESET}")
        
        print_section(f"{lang['current']} {lang['theme']}: {Colors.BOLD}{config.theme.upper()}{Colors.RESET}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        
        # Show all options with navigation
        for i, option in enumerate(all_options):
            option_type, option_key = option_map[i]
            
            # Skip separators in selection
            if option_type == 'separator':
                print(f"{Colors.BORDER}{option}{Colors.RESET}")
                continue
            
            # Check if in preview mode
            in_preview = option_key and option_key in preview_mode
            
            if i == selected:
                # Highlighted item
                if in_preview:
                    print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.YELLOW}▶{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}{option}{Colors.RESET} {Colors.DIM}(Preview - Enter again to apply){Colors.RESET}")
                else:
                    print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.GREEN}▶{Colors.RESET} {Colors.BOLD}{Colors.CYAN}{option}{Colors.RESET}")
            else:
                # Normal item
                if in_preview:
                    print(f"{Colors.MAGENTA}│{Colors.RESET}   {Colors.DIM}{option} (Previewing){Colors.RESET}")
                else:
                    print(f"{Colors.MAGENTA}│{Colors.RESET}   {Colors.TEXT}{option}{Colors.RESET}")
        
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        
        if ARROW_KEYS_AVAILABLE:
            print(f"\n{Colors.DIM}↑↓: Navigate | Enter: Preview/Apply | ESC: Cancel{Colors.RESET}")
        else:
            print(f"\n{Colors.DIM}Enter number to select{Colors.RESET}")
        
        # Get input
        if ARROW_KEYS_AVAILABLE:
            key = get_key()
            
            if key == 'up':
                # Move up, skip separators
                selected = (selected - 1) % len(all_options)
                while option_map[selected][0] == 'separator':
                    selected = (selected - 1) % len(all_options)
            
            elif key == 'down':
                # Move down, skip separators
                selected = (selected + 1) % len(all_options)
                while option_map[selected][0] == 'separator':
                    selected = (selected + 1) % len(all_options)
            
            elif key == 'enter':
                option_type, option_key = option_map[selected]
                
                if option_type == 'theme':
                    if option_key in preview_mode:
                        # Second enter - apply theme
                        config.theme = option_key
                        config.save()
                        refresh_colors()
                        lang = config.get_lang()
                        preview_mode.clear()
                        animate_loading(f"{lang['apply']} theme...", 0.5)
                    else:
                        # First enter - preview theme
                        preview_mode[option_key] = True
                        # Temporarily apply theme
                        old_theme = config.theme
                        config.theme = option_key
                        refresh_colors()
                
                elif option_type == 'language':
                    config.language = option_key
                    config.save()
                    lang = config.get_lang()
                    preview_mode.clear()
                    animate_loading(f"{lang['apply']}...", 0.5)
                
                elif option_type == 'back':
                    return
            
            elif key == 'esc':
                # Cancel any previews
                if preview_mode:
                    # Restore original theme
                    refresh_colors()
                    lang = config.get_lang()
                    preview_mode.clear()
                else:
                    return
        
        else:
            # Fallback to number input
            try:
                choice = get_input("Choose option", Colors.MAGENTA)
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                # Map number to non-separator options
                valid_options = [(i, opt) for i, opt in enumerate(option_map) if opt[0] != 'separator']
                
                if 1 <= choice_num <= len(valid_options):
                    idx, (option_type, option_key) = valid_options[choice_num - 1]
                    
                    if option_type == 'theme':
                        config.theme = option_key
                        config.save()
                        refresh_colors()
                        lang = config.get_lang()
                        animate_loading(f"{lang['apply']} theme...", 0.5)
                    
                    elif option_type == 'language':
                        config.language = option_key
                        config.save()
                        lang = config.get_lang()
                        animate_loading(f"{lang['apply']}...", 0.5)
                    
                    elif option_type == 'back':
                        return
                
                else:
                    print_error(lang['invalid_choice'])
                    time.sleep(1)
            
            except ValueError:
                print_error(lang['invalid_choice'])
                time.sleep(1)
            except KeyboardInterrupt:
                return

# Cấu hình
EXCLUDED_FOLDERS = {
    '$RECYCLE.BIN', 'System Volume Information', 'Recovery', 
    '$WinREAgent', 'hiberfil.sys', 'pagefile.sys', 'swapfile.sys',
    'Windows', 'Program Files', 'Program Files (x86)', 'ProgramData'
}

EXCLUDED_EXTENSIONS = {'.tmp', '.temp', '.cache', '.lock'}

MAX_WORKERS = 4  # Số luồng song song
CHUNK_SIZE = 1024 * 1024  # 1MB cho việc đọc file khi hash
LOG_FILE = 'file_sync.log'
STATE_FILE = 'sync_state.json'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FileSyncStats:
    """Thống kê quá trình sync"""
    def __init__(self):
        self.scanned_files = 0
        self.new_files = 0
        self.updated_files = 0
        self.copied_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.total_size = 0
        self.copied_size = 0
        self.lock = threading.Lock()
    
    def increment(self, attr, value=1):
        with self.lock:
            setattr(self, attr, getattr(self, attr) + value)
    
    def get_summary(self):
        return {
            'scanned': self.scanned_files,
            'new': self.new_files,
            'updated': self.updated_files,
            'copied': self.copied_files,
            'failed': self.failed_files,
            'skipped': self.skipped_files,
            'total_size_gb': self.total_size / (1024**3),
            'copied_size_gb': self.copied_size / (1024**3)
        }

class FileInfo:
    """Thông tin chi tiết về file"""
    def __init__(self, path: Path):
        self.path = path
        try:
            stat = path.stat()
            self.size = stat.st_size
            self.mtime = stat.st_mtime
            self.exists = True
        except (OSError, PermissionError):
            self.size = 0
            self.mtime = 0
            self.exists = False
    
    def needs_update(self, other: 'FileInfo') -> bool:
        """Kiểm tra xem file có cần update không"""
        if not other.exists:
            return True
        if self.size != other.size:
            return True
        # Cho phép sai lệch 2 giây do file system khác nhau
        if abs(self.mtime - other.mtime) > 2:
            return True
        return False
    
    def calculate_hash(self, algorithm='md5') -> Optional[str]:
        """Tính hash của file (chỉ dùng khi cần thiết)"""
        if not self.exists:
            return None
        
        try:
            hasher = hashlib.new(algorithm)
            with open(self.path, 'rb') as f:
                while chunk := f.read(CHUNK_SIZE):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logging.error(f"Không thể tính hash cho {self.path}: {e}")
            return None

class SyncState:
    """Quản lý trạng thái sync để có thể resume"""
    def __init__(self, state_file: str = STATE_FILE):
        self.state_file = state_file
        self.completed_files: Set[str] = set()
        self.load()
    
    def load(self):
        """Load trạng thái từ file"""
        if Path(self.state_file).exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_files = set(data.get('completed_files', []))
                logging.info(f"Đã load trạng thái: {len(self.completed_files)} file đã hoàn thành")
            except Exception as e:
                logging.warning(f"Không thể load trạng thái: {e}")
    
    def save(self):
        """Lưu trạng thái vào file"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'completed_files': list(self.completed_files),
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Không thể lưu trạng thái: {e}")
    
    def mark_completed(self, relative_path: str):
        """Đánh dấu file đã hoàn thành"""
        self.completed_files.add(relative_path)
    
    def is_completed(self, relative_path: str) -> bool:
        """Kiểm tra file đã hoàn thành chưa"""
        return relative_path in self.completed_files
    
    def clear(self):
        """Xóa trạng thái"""
        self.completed_files.clear()
        if Path(self.state_file).exists():
            Path(self.state_file).unlink()

def should_exclude(path: Path) -> bool:
    """Kiểm tra có nên bỏ qua file/folder này không"""
    # Kiểm tra folder
    for part in path.parts:
        if part in EXCLUDED_FOLDERS:
            return True
    
    # Kiểm tra extension
    if path.suffix.lower() in EXCLUDED_EXTENSIONS:
        return True
    
    # Kiểm tra file ẩn trên Windows
    try:
        if os.name == 'nt':
            import stat
            if path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN:
                return True
    except:
        pass
    
    return False

def scan_drive_fast(drive_path: Path, stats: FileSyncStats) -> Dict[str, FileInfo]:
    """Quét ổ đĩa nhanh với xử lý song song"""
    files_dict = {}
    
    if not drive_path.exists():
        logging.error(f"Ổ đĩa {drive_path} không tồn tại!")
        return files_dict
    
    logging.info(f"Đang quét ổ {drive_path}...")
    
    try:
        for root, dirs, files in os.walk(drive_path, topdown=True):
            root_path = Path(root)
            
            # Loại bỏ các thư mục không cần quét
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                
                # Skip file bị loại trừ
                if should_exclude(file_path):
                    continue
                
                try:
                    relative_path = file_path.relative_to(drive_path)
                    file_info = FileInfo(file_path)
                    
                    if file_info.exists:
                        files_dict[str(relative_path)] = file_info
                        stats.increment('scanned_files')
                        stats.increment('total_size', file_info.size)
                        
                except (ValueError, OSError, PermissionError) as e:
                    logging.debug(f"Bỏ qua {file_path}: {e}")
                    continue
    
    except KeyboardInterrupt:
        logging.warning("Quét bị gián đoạn bởi người dùng")
        raise
    except Exception as e:
        logging.error(f"Lỗi khi quét: {e}")
    
    return files_dict

def copy_file_with_retry(source: Path, dest: Path, retries: int = 3) -> bool:
    """Copy file với retry"""
    for attempt in range(retries):
        try:
            # Tạo thư mục đích
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, dest)
            
            # Verify size
            if source.stat().st_size != dest.stat().st_size:
                raise Exception("Kích thước file không khớp sau khi copy")
            
            return True
            
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Thử lại lần {attempt + 2}/{retries} cho {source.name}")
                continue
            else:
                logging.error(f"Không thể copy {source} -> {dest}: {e}")
                return False
    
    return False

def copy_single_file(args: Tuple) -> Tuple[str, bool, int]:
    """Copy một file (để dùng với ThreadPoolExecutor)"""
    relative_path, source_file, dest_file, verify_hash = args
    
    try:
        # Verify bằng hash nếu cần
        if verify_hash and dest_file.exists():
            source_hash = source_file.calculate_hash()
            dest_hash = FileInfo(dest_file).calculate_hash()
            if source_hash == dest_hash:
                return (relative_path, True, 0)
        
        size = source_file.size
        success = copy_file_with_retry(source_file.path, dest_file)
        
        return (relative_path, success, size if success else 0)
        
    except Exception as e:
        logging.error(f"Lỗi khi copy {relative_path}: {e}")
        return (relative_path, False, 0)

def sync_drives(source_drive: str, dest_drive: str, 
                dry_run: bool = True,
                verify_hash: bool = False,
                resume: bool = True,
                parallel: bool = True) -> FileSyncStats:
    """
    Sync ổ đĩa với nhiều tùy chọn
    """
    
    source_drive = Path(source_drive)
    dest_drive = Path(dest_drive)
    stats = FileSyncStats()
    state = SyncState() if resume else None
    
    # Kiểm tra ổ đĩa
    if not source_drive.exists():
        print_error(f"Ổ đĩa nguồn {source_drive} không tồn tại!")
        return stats
    
    if not dest_drive.exists():
        print_error(f"Ổ đĩa đích {dest_drive} không tồn tại!")
        return stats
    
    print_section(f"{'DRY RUN' if dry_run else 'SYNC MODE'}")
    print_item("📦", "Nguồn:", str(source_drive))
    print_item("📂", "Đích:", str(dest_drive))
    print_item("🔐", "Verify hash:", "Yes" if verify_hash else "No")
    print_item("⚡", "Parallel:", "Yes" if parallel else "No")
    print_item("↻", "Resume:", "Yes" if resume else "No")
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    # Quét ổ đĩa
    print_section("Quét ổ đĩa")
    animate_loading(f"Đang quét {source_drive}", 0.5)
    source_files = scan_drive_fast(source_drive, stats)
    
    animate_loading(f"Đang quét {dest_drive}", 0.5)
    dest_stats = FileSyncStats()
    dest_files = scan_drive_fast(dest_drive, dest_stats)
    
    print_item(Colors.CHECK, f"Nguồn:", f"{stats.scanned_files:,} files ({stats.total_size / (1024**3):.2f} GB)")
    print_item(Colors.CHECK, f"Đích:", f"{dest_stats.scanned_files:,} files ({dest_stats.total_size / (1024**3):.2f} GB)")
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    # Phân tích sự khác biệt
    print_section("Phân tích sự khác biệt")
    animate_loading("Đang so sánh files", 0.5)
    files_to_copy = []
    
    for relative_path, source_info in source_files.items():
        # Skip nếu đã hoàn thành
        if state and state.is_completed(relative_path):
            stats.increment('skipped_files')
            continue
        
        dest_path = dest_drive / relative_path
        dest_info = FileInfo(dest_path)
        
        if source_info.needs_update(dest_info):
            if not dest_info.exists:
                stats.increment('new_files')
            else:
                stats.increment('updated_files')
            
            files_to_copy.append((
                relative_path,
                source_info,
                dest_path,
                verify_hash
            ))
    
    print_item(Colors.STAR, "File mới:", f"{stats.new_files:,}")
    print_item(Colors.DOT, "Cần cập nhật:", f"{stats.updated_files:,}")
    print_item(Colors.ARROW, "Đã bỏ qua:", f"{stats.skipped_files:,}")
    print_item(Colors.CHECK, "Tổng xử lý:", f"{len(files_to_copy):,}")
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    if not files_to_copy:
        print_success("Không có gì cần copy! Mọi thứ đã đồng bộ ✨")
        return stats
    
    if dry_run:
        print_section("Preview (10 files đầu)")
        for i, (rel_path, src_info, _, _) in enumerate(files_to_copy[:10]):
            print_item(Colors.ARROW, f"{rel_path}", f"({src_info.size / (1024**2):.2f} MB)")
        
        if len(files_to_copy) > 10:
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.DIM}... và {len(files_to_copy) - 10} file khác{Colors.RESET}")
        
        total_size = sum(src.size for _, src, _, _ in files_to_copy)
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        print_info(f"Tổng dung lượng: {Colors.BOLD}{total_size / (1024**3):.2f} GB{Colors.RESET}")
        print_warning("Đây chỉ là DRY RUN. Chọn option 3 hoặc 4 để sync thực sự.")
        return stats
    
    # Copy files
    print_section(f"Bắt đầu copy {len(files_to_copy):,} files")
    
    if parallel and MAX_WORKERS > 1:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(copy_single_file, args): args[0] 
                      for args in files_to_copy}
            
            for i, future in enumerate(as_completed(futures), 1):
                relative_path, success, size = future.result()
                
                if success:
                    stats.increment('copied_files')
                    stats.increment('copied_size', size)
                    if state:
                        state.mark_completed(relative_path)
                else:
                    stats.increment('failed_files')
                
                # Update progress
                if i % 10 == 0 or i == len(files_to_copy):
                    print_progress(i, len(files_to_copy), "Progress")
                
                # Lưu trạng thái mỗi 100 file
                if state and stats.copied_files % 100 == 0:
                    state.save()
    else:
        for i, args in enumerate(files_to_copy, 1):
            relative_path, success, size = copy_single_file(args)
            
            if success:
                stats.increment('copied_files')
                stats.increment('copied_size', size)
                if state:
                    state.mark_completed(relative_path)
            else:
                stats.increment('failed_files')
            
            if i % 10 == 0 or i == len(files_to_copy):
                print_progress(i, len(files_to_copy), "Progress")
    
    print()  # New line after progress
    
    # Lưu trạng thái cuối cùng
    if state:
        state.save()
    
    # Tổng kết
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    print_header("HOÀN THÀNH")
    summary = stats.get_summary()
    print_item(Colors.CHECK, "Files đã copy:", f"{summary['copied']:,}")
    print_item(Colors.CROSS if summary['failed'] > 0 else Colors.CHECK, "Files thất bại:", f"{summary['failed']:,}")
    print_item(Colors.STAR, "Dung lượng:", f"{summary['copied_size_gb']:.2f} GB")
    print_item(Colors.DOT, "Hoàn thành lúc:", datetime.now().strftime('%H:%M:%S'))
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    if summary['failed'] > 0:
        print_warning(f"Có {summary['failed']} file lỗi. Xem log để biết chi tiết.")
    
    return stats

def compare_drives(drive1: str, drive2: str):
    """So sánh 2 ổ đĩa và hiển thị sự khác biệt"""
    print_section("So sánh hai ổ đĩa")
    
    animate_loading(f"Đang quét {drive1}", 0.5)
    stats1 = FileSyncStats()
    files1 = scan_drive_fast(Path(drive1), stats1)
    
    animate_loading(f"Đang quét {drive2}", 0.5)
    stats2 = FileSyncStats()
    files2 = scan_drive_fast(Path(drive2), stats2)
    
    only_in_1 = set(files1.keys()) - set(files2.keys())
    only_in_2 = set(files2.keys()) - set(files1.keys())
    in_both = set(files1.keys()) & set(files2.keys())
    
    different = []
    for rel_path in in_both:
        if files1[rel_path].needs_update(files2[rel_path]):
            different.append(rel_path)
    
    print_item(Colors.STAR, "Chỉ có ở " + drive1, f"{len(only_in_1):,} files")
    print_item(Colors.STAR, "Chỉ có ở " + drive2, f"{len(only_in_2):,} files")
    print_item(Colors.CHECK, "Có ở cả hai", f"{len(in_both):,} files")
    print_item(Colors.DOT, "Khác nhau", f"{len(different):,} files")
    print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    if only_in_1:
        print_section(f"Files chỉ có ở {drive1} (10 đầu)")
        for i, path in enumerate(list(only_in_1)[:10], 1):
            print_item(Colors.ARROW, path, "")
        if len(only_in_1) > 10:
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.DIM}... và {len(only_in_1) - 10} file khác{Colors.RESET}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
    
    if different:
        print_section("Files khác nhau (10 đầu)")
        for i, path in enumerate(different[:10], 1):
            f1 = files1[path]
            f2 = files2[path]
            print_item(Colors.DOT, path, "")
            print(f"{Colors.MAGENTA}│{Colors.RESET}   {Colors.DIM}{drive1}: {f1.size / (1024**2):.2f} MB{Colors.RESET}")
            print(f"{Colors.MAGENTA}│{Colors.RESET}   {Colors.DIM}{drive2}: {f2.size / (1024**2):.2f} MB{Colors.RESET}")
        if len(different) > 10:
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.DIM}... và {len(different) - 10} file khác{Colors.RESET}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")

def get_available_drives():
    """Lấy danh sách các ổ đĩa có sẵn"""
    drives = []
    
    if os.name == 'nt':  # Windows
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if Path(drive).exists():
                try:
                    # Lấy thông tin ổ đĩa
                    total, used, free = shutil.disk_usage(drive)
                    drives.append({
                        'path': drive,
                        'letter': letter,
                        'total_gb': total / (1024**3),
                        'free_gb': free / (1024**3),
                        'used_gb': used / (1024**3)
                    })
                except:
                    pass
    else:  # Linux/Mac
        # Thêm logic cho Unix-like systems
        drives.append({'path': '/', 'letter': 'Root'})
    
    return drives

def select_drive(prompt: str, exclude_drive: str = None) -> str:
    """Cho phép người dùng chọn ổ đĩa từ danh sách"""
    drives = get_available_drives()
    
    if not drives:
        print_error(lang['no_drives'])
        return None
    
    print_section(prompt)
    
    available_drives = []
    drive_display = []
    
    for i, drive in enumerate(drives):
        # Bỏ qua ổ đĩa đã chọn (nếu có)
        if exclude_drive and drive['path'] == exclude_drive:
            continue
        
        available_drives.append(drive)
        used_percent = (drive['used_gb'] / drive['total_gb'] * 100)
        bar_filled = int(20 * drive['used_gb'] / drive['total_gb'])
        bar = '█' * bar_filled + '░' * (20 - bar_filled)
        
        # Format display string
        display = (f"{Colors.BOLD}{Colors.CYAN}{drive['path']:<6}{Colors.RESET} "
                  f"{Colors.BORDER}{bar}{Colors.RESET} "
                  f"{Colors.TEXT}{drive['free_gb']:>6.1f}GB {lang['free']}{Colors.RESET} "
                  f"{Colors.DIM}({used_percent:.0f}% {lang['used']}){Colors.RESET}")
        drive_display.append(display)
    
    if not available_drives:
        print_error(lang['no_drives'])
        return None
    
    # Add custom path option
    drive_display.append(f"{Colors.TEXT}{lang['custom_path']}{Colors.RESET}")
    
    # Show with arrow navigation if available
    if ARROW_KEYS_AVAILABLE:
        selected_idx = select_with_arrows(drive_display, prompt)
        if selected_idx == -1:
            return None
        
        if selected_idx == len(available_drives):
            # Custom path
            clear_screen()
            print_section(prompt)
            custom_path = get_input(lang['enter_path'], Colors.CYAN)
            if custom_path and Path(custom_path).exists():
                return custom_path
            else:
                print_error(lang['path_not_exist'])
                time.sleep(1)
                return None
        else:
            selected = available_drives[selected_idx]['path']
            animate_loading(f"{lang['selecting']} {selected}", 0.5)
            return selected
    else:
        # Fallback to number input
        for i, display in enumerate(drive_display, 1):
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.YELLOW}{i}.{Colors.RESET} {display}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        
        while True:
            try:
                choice = get_input(lang['choose_drive'], Colors.MAGENTA)
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                if choice_num == len(available_drives) + 1:
                    # Custom path
                    custom_path = get_input(lang['enter_path'], Colors.CYAN)
                    if custom_path and Path(custom_path).exists():
                        return custom_path
                    else:
                        print_error(lang['path_not_exist'])
                        continue
                
                if 1 <= choice_num <= len(available_drives):
                    selected = available_drives[choice_num - 1]['path']
                    animate_loading(f"{lang['selecting']} {selected}", 0.5)
                    return selected
                else:
                    print_error(lang['invalid_choice'])
            
            except ValueError:
                print_error(lang['invalid_choice'])
            except KeyboardInterrupt:
                print_error(f"\n{lang['cancelled']}")
                return None

if __name__ == "__main__":
    clear_screen()
    
    # Refresh theme and language
    refresh_colors()
    
    # ASCII Art Banner
    banner = [
        f"{Colors.CYAN}  ███████╗██╗██╗     ███████╗    ███████╗██╗   ██╗███╗   ██╗ ██████╗{Colors.RESET}",
        f"{Colors.CYAN}  ██╔════╝██║██║     ██╔════╝    ██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝{Colors.RESET}",
        f"{Colors.BLUE}  █████╗  ██║██║     █████╗      ███████╗ ╚████╔╝ ██╔██╗ ██║██║     {Colors.RESET}",
        f"{Colors.BLUE}  ██╔══╝  ██║██║     ██╔══╝      ╚════██║  ╚██╔╝  ██║╚██╗██║██║     {Colors.RESET}",
        f"{Colors.MAGENTA}  ██║     ██║███████╗███████╗    ███████║   ██║   ██║ ╚████║╚██████╗{Colors.RESET}",
        f"{Colors.MAGENTA}  ╚═╝     ╚═╝╚══════╝╚══════╝    ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝{Colors.RESET}",
    ]
    
    for line in banner:
        print(line)
    
    # Main menu - Choose between Sync or Settings
    print_header(lang['select_action'])
    
    main_menu = [
        f"🚀 {lang['menu_sync']} - {lang['menu_sync_desc']}",
        f"⚙️  {lang['menu_settings']} - {lang['menu_settings_desc']}",
        f"✗  {lang['menu_exit']} - {lang['menu_exit_desc']}"
    ]
    
    if ARROW_KEYS_AVAILABLE:
        main_choice = select_with_arrows(main_menu, lang['select_action'])
        if main_choice == -1 or main_choice == 2:
            print_info(f"{lang['goodbye']} 👋")
            exit(0)
        elif main_choice == 1:
            # Go to settings
            show_settings()
            clear_screen()
            print_info("Settings saved! Restart to continue.")
            exit(0)
    else:
        # Fallback to number selection
        for i, item in enumerate(main_menu, 1):
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.YELLOW}{i}.{Colors.RESET} {Colors.TEXT}{item}{Colors.RESET}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        
        choice = get_input(lang['choose_action'], Colors.MAGENTA)
        
        if choice == '2':
            show_settings()
            clear_screen()
            print_info("Settings saved! Restart to continue.")
            exit(0)
        elif choice == '3' or choice == '0':
            print_info(f"{lang['goodbye']} 👋")
            exit(0)
    
    # Continue with sync flow
    clear_screen()
    
    # Show banner again
    for line in banner:
        print(line)
    
    print_header(lang['select_drive'])
    
    # Chọn ổ đĩa nguồn
    SOURCE = select_drive(f"📦 {lang['source']}")
    if not SOURCE:
        exit(1)
    
    clear_screen()
    for line in banner:
        print(line)
    
    print_success(f"{lang['selected_source']} {Colors.BOLD}{SOURCE}{Colors.RESET}")
    
    # Chọn ổ đĩa đích
    DEST = select_drive(f"📂 {lang['destination']}", exclude_drive=SOURCE)
    if not DEST:
        exit(1)
    
    clear_screen()
    for line in banner:
        print(line)
    
    print_success(f"{lang['selected_source']} {Colors.BOLD}{SOURCE}{Colors.RESET}")
    print_success(f"{lang['selected_dest']} {Colors.BOLD}{DEST}{Colors.RESET}")
    
    # Action menu
    print_header(lang['select_action'])
    
    action_menu = [
        f"🔍 {lang['menu_compare']} - {lang['menu_compare_desc']}",
        f"👁️  {lang['menu_preview']} - {lang['menu_preview_desc']}",
        f"⚡ {lang['menu_sync']} - {lang['menu_sync_desc']}",
        f"🔐 {lang['menu_secure']} - {lang['menu_secure_desc']}",
        f"🗑️  {lang['menu_clear']} - {lang['menu_clear_desc']}",
        f"↻  {lang['menu_reselect']} - {lang['menu_reselect_desc']}",
        f"✗  {lang['menu_exit']} - {lang['menu_exit_desc']}"
    ]
    
    if ARROW_KEYS_AVAILABLE:
        action_choice = select_with_arrows(action_menu, lang['select_action'])
    else:
        for i, item in enumerate(action_menu, 1):
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.YELLOW}{i}.{Colors.RESET} {Colors.TEXT}{item}{Colors.RESET}")
        print(f"{Colors.MAGENTA}╰{'─' * 76}{Colors.RESET}")
        
        choice = get_input(lang['choose_action'], Colors.MAGENTA)
        try:
            action_choice = int(choice) - 1
        except:
            action_choice = -1
    
    if action_choice == 0:  # Compare
        clear_screen()
        print_header(f"COMPARE: {SOURCE} ⇄ {DEST}")
        animate_loading(lang['comparing'], 1.0)
        compare_drives(SOURCE, DEST)
    
    elif action_choice == 1:  # Preview
        clear_screen()
        print_header(f"DRY RUN: {SOURCE} → {DEST}")
        animate_loading(lang['starting'], 0.8)
        sync_drives(SOURCE, DEST, dry_run=True)
    
    elif action_choice == 2:  # Quick sync
        clear_screen()
        print_header(f"SYNC: {SOURCE} → {DEST}")
        print_warning("All files from source will be copied to destination")
        print_box([
            f"Source: {SOURCE}",
            f"Destination: {DEST}",
            f"Mode: Parallel sync (fast)"
        ])
        confirm = get_input("Continue? (yes/no)", Colors.RED)
        if confirm.lower() in ['yes', 'y', 'có']:
            animate_loading(f"{lang['starting']} sync engine", 1.0)
            sync_drives(SOURCE, DEST, dry_run=False, parallel=True)
        else:
            print_error(lang['cancelled'])
    
    elif action_choice == 3:  # Secure sync
        clear_screen()
        print_header(f"SECURE SYNC: {SOURCE} → {DEST}")
        print_warning("Sync with hash verification - slower but accurate")
        print_box([
            f"Source: {SOURCE}",
            f"Destination: {DEST}",
            f"Mode: Verify MD5 hash for all files"
        ])
        confirm = get_input("Continue? (yes/no)", Colors.RED)
        if confirm.lower() in ['yes', 'y', 'có']:
            animate_loading(f"{lang['starting']} secure sync", 1.2)
            sync_drives(SOURCE, DEST, dry_run=False, verify_hash=True, parallel=True)
        else:
            print_error(lang['cancelled'])
    
    elif action_choice == 4:  # Clear state
        state = SyncState()
        state.clear()
        print_success("Resume state cleared")
    
    elif action_choice == 5:  # Reselect
        print_info("Restart program to reselect drives")
    
    elif action_choice == 6 or action_choice == -1:  # Exit
        print_info(f"{lang['goodbye']} 👋")
        exit(0)
    
    else:
        print_error(lang['invalid_choice'])
    
    print(f"\n{Colors.BORDER}{'─' * 80}{Colors.RESET}")
    get_input(lang['press_enter'], Colors.DIM)