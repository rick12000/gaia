"""Window management functionality for GAIA"""

import pyautogui
import time
from speech import speak
from ui_manager import show_confirmation_dialog

def minimize_window():
    """Minimize the current active window"""
    pyautogui.hotkey('win', 'down')
    print("Minimized current window")
    return True

def maximize_window():
    """Maximize/restore the current active window"""
    pyautogui.hotkey('win', 'up')
    print("Maximized current window")
    return True

def toggle_fullscreen():
    """Toggle fullscreen mode for current window (F11)"""
    pyautogui.press('f11')
    print("Toggled fullscreen mode")
    return True

def handle_close_confirmation(confirmed):
    """Handle the close confirmation response"""
    if confirmed:
        print("Close confirmed, closing window")
        # Alt+F4 to close window
        pyautogui.hotkey('alt', 'f4')
    else:
        print("Close canceled")

def close_window():
    """Close the current active window with confirmation"""
    speak("Are you sure you want to close this window?")
    show_confirmation_dialog(
        "Are you sure you want to close this window?",
        handle_close_confirmation
    )
    return True
