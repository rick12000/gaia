"""Spot/location management for GAIA"""

import json
import pyautogui
import os
from speech import speak
from ui_manager import show_label
import config

# Global spots dictionary
spots = {}

def save_spots():
    """Save spots to disk"""
    with open(config.SPOTS_FILE, "w") as f:
        json.dump(spots, f)

def load_spots():
    """Load spots from disk"""
    global spots
    if os.path.exists(config.SPOTS_FILE):
        with open(config.SPOTS_FILE, "r") as f:
            try:
                spots = json.load(f)
                # Convert spot coordinates from string back to integers if needed
                for name in spots:
                    if isinstance(spots[name], list):
                        spots[name] = tuple(spots[name])
                print(f"Loaded spots: {spots}")
            except Exception as e:
                print(f"Error loading spots: {e}")
                spots = {}
    return spots

def reset_spots():
    """Delete all spots"""
    global spots
    spots = {}
    if os.path.exists(config.SPOTS_FILE):
        os.remove(config.SPOTS_FILE)

def add_spot(name):
    """Add a new spot at current cursor position"""
    position = pyautogui.position()
    spots[name] = position
    save_spots()
    speak(f"Marked spot as {name}")
    show_label(name, *position)
    return True

def delete_spot(name):
    """Delete a spot by name"""
    if name in spots:
        del spots[name]
        save_spots()
        speak(f"Deleted mark {name}")
        return True
    else:
        speak(f"No spot named {name}")
        return False

def go_to_spot(name):
    """Move cursor to a spot"""
    if name in spots:
        x, y = spots[name]
        pyautogui.moveTo(x, y)
        return True
    else:
        speak(f"No spot named {name}")
        return False

def list_spots():
    """List all saved spots"""
    if not spots:
        speak("No spots saved.")
    else:
        names = ", ".join(spots.keys())
        speak(f"Saved spots: {names}")
    return spots

def get_spots():
    """Return the spots dictionary"""
    return spots
