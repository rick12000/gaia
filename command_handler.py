"""Command handling system for GAIA"""

import re
import time
import pyautogui
import pyperclip

from speech import speak
from input_commands import (
    start_key_hold, stop_key_hold, adjust_key_speed
)
from spot_manager import (
    add_spot, delete_spot, reset_spots, go_to_spot, list_spots, get_spots
)
from app_launcher import go_to_target
from ui_manager import visualize_spots
from window_manager import (
    minimize_window, maximize_window, toggle_fullscreen, close_window
)

# --- Number Handling Utilities ---
WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    'twenty one': 21, 'twenty two': 22, 'twenty three': 23, 'twenty four': 24, 'twenty five': 25, 'twenty six': 26, 'twenty seven': 27, 'twenty eight': 28, 'twenty nine': 29, 'thirty': 30,
    'thirty one': 31, 'thirty two': 32, 'thirty three': 33, 'thirty four': 34, 'thirty five': 35, 'thirty six': 36, 'thirty seven': 37, 'thirty eight': 38, 'thirty nine': 39, 'forty': 40,
    'forty one': 41, 'forty two': 42, 'forty three': 43, 'forty four': 44, 'forty five': 45, 'forty six': 46, 'forty seven': 47, 'forty eight': 48, 'forty nine': 49, 'fifty': 50,
    'fifty one': 51, 'fifty two': 52, 'fifty three': 53, 'fifty four': 54, 'fifty five': 55, 'fifty six': 56, 'fifty seven': 57, 'fifty eight': 58, 'fifty nine': 59, 'sixty': 60,
    'sixty one': 61, 'sixty two': 62, 'sixty three': 63, 'sixty four': 64, 'sixty five': 65, 'sixty six': 66, 'sixty seven': 67, 'sixty eight': 68, 'sixty nine': 69, 'seventy': 70,
    'seventy one': 71, 'seventy two': 72, 'seventy three': 73, 'seventy four': 74, 'seventy five': 75, 'seventy six': 76, 'seventy seven': 77, 'seventy eight': 78, 'seventy nine': 79, 'eighty': 80,
    'eighty one': 81, 'eighty two': 82, 'eighty three': 83, 'eighty four': 84, 'eighty five': 85, 'eighty six': 86, 'eighty seven': 87, 'eighty eight': 88, 'eighty nine': 89, 'ninety': 90,
    'ninety one': 91, 'ninety two': 92, 'ninety three': 93, 'ninety four': 94, 'ninety five': 95, 'ninety six': 96, 'ninety seven': 97, 'ninety eight': 98, 'ninety nine': 99, 'hundred': 100
}

def parse_number(text):
    """Converts digit string or number word (up to 100) to integer."""
    text = text.lower().strip()
    try:
        num = int(text)
        if 1 <= num <= 100:
            return num
        else:
            return None
    except ValueError:
        return WORD_TO_NUM.get(text)

# --- Regex Patterns ---
number_words_pattern_100 = '|'.join(WORD_TO_NUM.keys())
number_pattern_100 = rf'([1-9]|[1-9]\d|100|{number_words_pattern_100})'
up_down_regex = re.compile(rf'^{number_pattern_100}\s+(up|down)(\s+enter)?$', re.IGNORECASE)

tab_number_words = {k: v for k, v in WORD_TO_NUM.items() if v <= 10}
tab_number_words_pattern = '|'.join(tab_number_words.keys())
tab_number_pattern = rf'([1-9]|10|{tab_number_words_pattern})'
tab_regex = re.compile(rf'^(next|previous)\s+{tab_number_pattern}\s+tabs?(\s+enter)?$', re.IGNORECASE)

# --- State Variables ---
# Confirmation state
waiting_for_confirmation = False
confirmation_callback = None
# Key holding state
last_held_key = None
# Dictation state
is_dictating = False
dictation_buffer = "" # Still useful for potential full transcript logging if needed later
dictation_word_chunk = [] # Holds words for incremental pasting
dictation_start_time = 0
last_speech_time = 0
last_paste_time = 0 # Time the last chunk was pasted
DICTATION_MAX_DURATION = 600 # 10 minutes
DICTATION_INACTIVITY_TIMEOUT = 30 # 30 seconds

# --- Helper Functions ---

def handle_confirmation(response):
    """Handle yes/no confirmation responses"""
    global waiting_for_confirmation, confirmation_callback
    if not waiting_for_confirmation or not confirmation_callback:
        return False
        
    response = response.lower().strip()
    if response == "yes":
        confirmation_callback(True)
    elif response == "no":
        confirmation_callback(False)
    else:
        return False
        
    waiting_for_confirmation = False
    confirmation_callback = None
    return True

def register_confirmation(callback):
    """Register a callback for confirmation"""
    global waiting_for_confirmation, confirmation_callback
    waiting_for_confirmation = True
    confirmation_callback = callback

def start_dictation_mode():
    """Activates dictation mode."""
    global is_dictating, dictation_buffer, dictation_word_chunk, dictation_start_time, last_speech_time, last_paste_time
    if is_dictating:
        speak("Already in dictation mode.")
        return
    is_dictating = True
    dictation_buffer = "" # Reset buffer
    dictation_word_chunk = [] # Reset word chunk list
    now = time.time()
    dictation_start_time = now
    last_speech_time = now # Initialize last speech time
    last_paste_time = now # Initialize last paste time
    speak("Starting dictation.")
    print("--- Dictation Started ---")

def stop_dictation_mode(reason="command"):
    """Deactivates dictation mode and pastes any remaining words."""
    global is_dictating, dictation_buffer, dictation_word_chunk
    if not is_dictating:
        return # Not dictating, nothing to stop

    is_dictating = False

    # Paste any remaining words before clearing
    if dictation_word_chunk:
        try:
            remaining_text = " ".join(dictation_word_chunk)
            pyperclip.copy(remaining_text)
            pyautogui.hotkey('ctrl', 'v')
            # Optionally add a space if needed, but often not desired at the very end
            # pyautogui.press('space')
            print(f"Pasted final remaining chunk: '{remaining_text}'")
            time.sleep(0.05) # Brief pause after final paste
        except Exception as paste_err:
            print(f"Error pasting final dictation chunk: {paste_err}")

    dictation_word_chunk = [] # Clear the chunk
    dictation_buffer = "" # Clear the buffer

    feedback = f"Dictation stopped due to {reason}."
    print(f"--- Dictation Stopped ({reason}) ---")
    speak(feedback)

# --- Main Command Handler ---

def handle_command(command):
    """Process a voice command"""
    global last_held_key, is_dictating

    command = command.lower().strip()
    print(f"Heard: {command}")
    
    # --- Regular Command Handling (if not dictating) ---
    if waiting_for_confirmation:
        if handle_confirmation(command):
            return
    
    # Check for "start dictation" command
    if command == "start dictation":
        start_dictation_mode()
        return True # Command handled

    if command == "faster":
        adjust_key_speed(faster=True, factor=2.0)
        speak("Increasing speed")
        return True
        
    if command == "slower":
        adjust_key_speed(faster=False, factor=2.0)
        speak("Decreasing speed")
        return True
    
    if command == "stop":
        if stop_key_hold():
            print("Stopped ongoing action")
            if last_held_key == 'down':
                pyautogui.press('up')
            elif last_held_key == 'up':
                pyautogui.press('down')
            elif last_held_key == 'left':
                pyautogui.press('right')
            elif last_held_key == 'right':
                pyautogui.press('left')
            last_held_key = None
        return True
    
    if command == "mode":
        pyautogui.hotkey('ctrl', '.')
        return True
        
    if command == "microphone":
        pyautogui.hotkey('alt', 'n')
        return True
        
    if command == "context":
        pyautogui.hotkey('ctrl', '/')
        return True
        
    if command == "screenshot":
        pyautogui.hotkey('win', 'shift', 's')
        return True
    
    if command == "minimize window":
        minimize_window()
        return True
        
    if command == "maximize window":
        maximize_window()
        return True
        
    if command == "fullscreen":
        toggle_fullscreen()
        return True
        
    if command == "close window":
        close_window()
        return True
    
    if command == "new tab":
        pyautogui.hotkey('ctrl', 't')
        return True
        
    if command == "close tab":
        pyautogui.hotkey('ctrl', 'w')
        return True
        
    if command == "reopen tab":
        pyautogui.hotkey('ctrl', 'shift', 't')
        return True
    
    if command == "save":
        pyautogui.hotkey('ctrl', 's')
        return True
        
    if command == "copy":
        pyautogui.hotkey('ctrl', 'c')
        return True
        
    if command == "paste":
        pyautogui.hotkey('ctrl', 'v')
        return True
        
    if command == "select all":
        pyautogui.hotkey('ctrl', 'a')
        return True
    
    if command == "undo":
        pyautogui.hotkey('ctrl', 'z')
        return True
    
    if command == "redo":
        pyautogui.hotkey('ctrl', 'shift', 'z')
        return True
    
    if command == "zoom":
        pyautogui.hotkey('ctrl', '+')
        return True
    
    if command == "zoom out":
        pyautogui.hotkey('ctrl', '-')
        return True
    
    if command == "previous":
        pyautogui.hotkey('alt', 'left')
        return True
    
    if command == "next":
        pyautogui.hotkey('alt', 'right')
        return True
    
    if command in get_spots():
        x, y = get_spots()[command]
        pyautogui.moveTo(x, y)
        pyautogui.click()
        return True
            
    if command.startswith("double click ") and len(command) > 12:
        name = command[12:].strip()
        if name in get_spots():
            x, y = get_spots()[name]
            pyautogui.moveTo(x, y)
            pyautogui.doubleClick()
            return True
    
    if command == "click" or command == "left click":
        pyautogui.click()
        return True
    
    if command == "right click":
        pyautogui.rightClick()
        return True
        
    if command == "double click":
        pyautogui.doubleClick()
        return True
    
    if command == "triple click":
        pyautogui.click(clicks=3)
        return True
    
    up_down_match = up_down_regex.match(command)
    if up_down_match:
        number_str = up_down_match.group(1)
        direction = up_down_match.group(2).lower()
        has_enter = up_down_match.group(3) is not None

        count = parse_number(number_str)

        if count and 1 <= count <= 100:
            for _ in range(count):
                pyautogui.press(direction)
                time.sleep(0.01)

            if has_enter:
                pyautogui.press('enter')

            print(f"Pressed {direction} {count} times{' plus Enter' if has_enter else ''}")
            return True
        else:
            print(f"Invalid number or range for up/down: {number_str}")
            return True

    if command == "left":
        pyautogui.press('left')
        return True
        
    if command == "right":
        pyautogui.press('right')
        return True
    
    if command == "p up":
        pyautogui.press('pageup')
        return True
        
    if command == "p down":
        pyautogui.press('pagedown')
        return True
    
    if command == "enter":
        pyautogui.press('enter')
        return True
        
    if command == "delete":
        pyautogui.press('delete')
        return True
        
    if command == "escape":
        pyautogui.press('escape')
        return True
        
    if command == "tab":
        pyautogui.press('tab')
        return True
        
    if command == "space":
        pyautogui.press('space')
        return True

    if command == "next edit":
        pyautogui.hotkey('alt', 'f5')
        return True
        
    if command == "previous edit":
        pyautogui.hotkey('shift', 'alt', 'f5')
        return True
    
    if command == "press down":
        last_held_key = 'down'
        start_key_hold('down')
        return True
        
    if command == "press up":
        last_held_key = 'up'
        start_key_hold('up')
        return True
    
    if command == "press left":
        last_held_key = 'left'
        start_key_hold('left')
        return True
    
    if command == "press right":
        last_held_key = 'right'
        start_key_hold('right')
        return True

    if command == "press page down":
        start_key_hold('pagedown', use_page_timing=True, page_interval=10.0)
        speak("Scrolling down slowly")
        return True
        
    if command == "press page up":
        start_key_hold('pageup', use_page_timing=True, page_interval=10.0)
        speak("Scrolling up slowly")
        return True
    
    if command == "select from":
        start_key_hold('down', with_shift=True)
        speak("Selecting downward")
        return True
        
    if command == "select until":
        start_key_hold('up', with_shift=True)
        speak("Selecting upward")
        return True
    
    if command == "next tab":
        pyautogui.hotkey('ctrl', 'tab')
        return True
        
    if command == "previous tab":
        pyautogui.hotkey('ctrl', 'shift', 'tab')
        return True

    tab_match = tab_regex.match(command)
    if tab_match:
        direction = tab_match.group(1).lower()
        number_str = tab_match.group(2)
        has_enter = tab_match.group(3) is not None

        count = parse_number(number_str)

        if count and 1 <= count <= 10:
            hotkey = ('ctrl', 'tab') if direction == 'next' else ('ctrl', 'shift', 'tab')
            for _ in range(count):
                pyautogui.hotkey(*hotkey)
                time.sleep(0.05)

            if has_enter:
                pyautogui.press('enter')

            print(f"Switched {direction} {count} tabs{' plus Enter' if has_enter else ''}")
            return True
        else:
            print(f"Invalid number or range for tab navigation: {number_str}")
            return True

    if command.startswith("look for "):
        search_term = command[9:].strip() # Get text after "look for "
        if search_term:
            pyperclip.copy(search_term)
            pyautogui.hotkey('ctrl', 'f') # Press Ctrl+F to open find
            time.sleep(0.2) # Wait a moment for the find bar/dialog to appear
            pyautogui.hotkey('ctrl', 'v') # Paste the search term
            print(f"Looking for: '{search_term}'")
        else:
            speak("Please specify what you want to look for.")
        return True

    if command.startswith("type "):
        text_to_type = command[5:].strip()
        if text_to_type:
            pyperclip.copy(text_to_type)
            pyautogui.hotkey('ctrl', 'v')
            print(f"Typing: {text_to_type}")
        return True
    
    if command == "search bar":
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.1)
        pyautogui.press('f6')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'f')
        speak("Activated search bar")
        print("Activated search bar")
        return True
    
    if command == "save all code":
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.1)
        pyautogui.press('s')
        print("Saving all files in VS Code")
        return True
    
    if command.startswith("goto line "):
        try:
            line_number = command[10:].strip()
            if line_number.isdigit():
                pyautogui.hotkey('ctrl', 'g')
                time.sleep(0.2)
                pyautogui.write(line_number)
                pyautogui.press('enter')
                print(f"Going to line {line_number}")
            else:
                speak("Invalid line number")
        except Exception as e:
            print(f"Error going to line: {e}")
        return True
    
    if command == "file down":
        pyautogui.hotkey('alt', 'down')
        return True
        
    if command == "file up":
        pyautogui.hotkey('alt', 'up')
        return True
    
    if command == "list spots":
        list_spots()
        return True
    
    if command == "reset spots":
        reset_spots()
        speak("All spots have been deleted.")
        return True
    
    if command == "visualize marks":
        visualize_spots(get_spots(), adjust_for_titlebar=True)
        speak("Showing marks")
        return True
        
    if command.startswith("mark delete "):
        name = command[12:].strip()
        delete_spot(name)
        return True
    
    if command.startswith("unmark "):
        name = command[7:].strip()
        delete_spot(name)
        return True
        
    if command.startswith("mark "):
        name = command[5:].strip()
        if not name:
            speak("Please specify a name for the mark")
            return True
        
        try:
            from config import protected_names
        except ImportError:
            print("Warning: protected_names not found in config, using defaults")
        
        if name in protected_names:
            speak(f"'{name}' is a protected name.")
        else:
            add_spot(name)
        return True
    
    if command in {"exit", "quit"}:
        speak("Goodbye.")
        import os
        os._exit(0)
    
    return False
