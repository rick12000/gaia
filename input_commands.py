"""Keyboard, mouse, and selection commands for GAIA"""

import pyautogui
import threading
import time
from speech import speak
import config

# Globals
key_hold_thread = None
key_hold_active = False
key_speed_lock = threading.Lock()

# Current key speed multiplier
KEY_SPEED_MULTIPLIER = config.KEY_SPEED_MULTIPLIER

def smooth_scroll(direction, use_page_timing=False):
    """Smoothly scroll up or down
    
    Parameters:
        direction: 'up' or 'down'
        use_page_timing: Use slower timing for page keys
    """
    global key_hold_active
    key_hold_active = True
    
    # Select the appropriate timing parameters
    if use_page_timing:
        base_interval = config.PAGE_KEY_RELEASE_INTERVAL
        scroll_amount = 15  # Larger steps for page scrolling
        print(f"Starting smooth scrolling: {direction} (page timing)")
    else:
        base_interval = config.KEY_RELEASE_INTERVAL
        scroll_amount = 8  # Smaller steps for smooth scrolling
        print(f"Starting smooth scrolling: {direction}")
    
    try:
        while key_hold_active:
            # Get current speed settings (thread-safe)
            with key_speed_lock:
                current_interval = base_interval / KEY_SPEED_MULTIPLIER
            
            # Scroll smoothly
            if direction == 'down':
                pyautogui.scroll(-scroll_amount)  # Negative for down
            else:  # up
                pyautogui.scroll(scroll_amount)   # Positive for up
                
            time.sleep(current_interval)
    except Exception as e:
        print(f"Error during smooth scrolling: {e}")
    finally:
        print(f"Stopped smooth scrolling: {direction}")

def hold_key(key, use_page_timing=False, with_shift=False):
    """Hold a key with repeated presses
    
    Parameters:
        key: The key to hold
        use_page_timing: Use slower timing for page keys
        with_shift: Hold shift key while pressing the key (for selection)
    """
    global key_hold_active
    key_hold_active = True
    
    # Use smooth scrolling for up/down
    if key in ['up', 'down'] and not with_shift:
        smooth_scroll(key, use_page_timing)
        return
    
    # Select the appropriate timing parameters
    if use_page_timing:
        base_press_interval = config.PAGE_KEY_PRESS_INTERVAL
        base_release_interval = config.PAGE_KEY_RELEASE_INTERVAL
        print(f"Starting to hold key: {key} (with page timing)")
    else:
        base_press_interval = config.KEY_PRESS_INTERVAL
        base_release_interval = config.KEY_RELEASE_INTERVAL
        print(f"Starting to hold key: {key}")
    
    try:
        # If selection mode, press and hold shift first
        if with_shift:
            pyautogui.keyDown('shift')
            print("Shift key pressed - selection active")
            
        while key_hold_active:
            # Get current speed settings (thread-safe)
            with key_speed_lock:
                current_press_interval = base_press_interval / KEY_SPEED_MULTIPLIER
                current_release_interval = base_release_interval / KEY_SPEED_MULTIPLIER
            
            # Press and release the key at current speed
            pyautogui.keyDown(key)
            time.sleep(current_press_interval)
            pyautogui.keyUp(key)
            time.sleep(current_release_interval)
    except Exception as e:
        print(f"Error holding key: {e}")
    finally:
        try:
            # Ensure keys are released
            pyautogui.keyUp(key)
            # Release shift if we were in selection mode
            if with_shift:
                pyautogui.keyUp('shift')
                print("Shift key released - selection complete")
        except:
            pass
        print(f"Stopped holding key: {key}")

def adjust_key_speed(faster=True):
    """Adjust the key repeat speed (faster or slower)"""
    global KEY_SPEED_MULTIPLIER
    
    with key_speed_lock:
        if faster:
            KEY_SPEED_MULTIPLIER += config.SPEED_INCREMENT
            print(f"Increased speed to {KEY_SPEED_MULTIPLIER:.2f}x")
            speak(f"Speed {KEY_SPEED_MULTIPLIER:.1f}")
        else:
            # Allow for much slower speeds
            KEY_SPEED_MULTIPLIER = max(config.MIN_SPEED_MULTIPLIER, KEY_SPEED_MULTIPLIER - config.SPEED_INCREMENT)
            print(f"Decreased speed to {KEY_SPEED_MULTIPLIER:.2f}x")
            speak(f"Speed {KEY_SPEED_MULTIPLIER:.1f}")

def stop_key_hold():
    """Stop any ongoing key hold operation"""
    global key_hold_active, key_hold_thread, KEY_SPEED_MULTIPLIER
    active = False
    
    if key_hold_active:
        key_hold_active = False
        if key_hold_thread and key_hold_thread.is_alive():
            key_hold_thread.join(timeout=1.0)
        active = True
        
    # Reset speed multiplier when stopping
    with key_speed_lock:
        KEY_SPEED_MULTIPLIER = 1.0
            
    return active

def start_key_hold(key, use_page_timing=False, with_shift=False):
    """Start holding a key in a separate thread"""
    global key_hold_thread, key_hold_active
    
    stop_key_hold()  # Stop any existing key hold
    key_hold_active = True
    key_hold_thread = threading.Thread(
        target=hold_key, 
        args=(key,), 
        kwargs={'use_page_timing': use_page_timing, 'with_shift': with_shift},
        daemon=True
    )
    key_hold_thread.start()
