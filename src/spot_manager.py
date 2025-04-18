"""Spot/location management for GAIA"""

import json
import pyautogui
import os
from speech import speak
from ui_manager import show_label
import config

# Global dictionary for single spots only
spots = {}

def save_spots():
    """Save spots to disk"""
    data_to_save = spots
    if not os.path.exists(config.USER_DATA_DIR):
        try:
            os.makedirs(config.USER_DATA_DIR)
            print(f"Created user data directory: {config.USER_DATA_DIR}")
        except Exception as e:
            print(f"Error creating user data directory {config.USER_DATA_DIR}: {e}")
            speak("Error saving configuration.")
            return

    try:
        with open(config.SPOTS_FILE, "w") as f:
            spots_serializable = {name: list(pos) for name, pos in spots.items()}
            json.dump(spots_serializable, f, indent=4)
    except Exception as e:
        print(f"Error saving spots file {config.SPOTS_FILE}: {e}")
        speak("Error saving spots.")

def load_spots():
    """Load spots from disk"""
    global spots
    if os.path.exists(config.SPOTS_FILE):
        try:
            with open(config.SPOTS_FILE, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict) and "spots" in loaded_data and "sequences" in loaded_data:
                    spots_loaded = loaded_data.get("spots", {})
                    print("Warning: Loading from newer format file, only spots will be used.")
                elif isinstance(loaded_data, dict):
                    spots_loaded = loaded_data
                else:
                    print(f"Warning: Unexpected format in {config.SPOTS_FILE}. Starting fresh.")
                    spots_loaded = {}

                spots = {name: tuple(pos) for name, pos in spots_loaded.items() if isinstance(pos, list) and len(pos) == 2}
                print(f"Loaded spots: {spots}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {config.SPOTS_FILE}: {e}")
            speak("Error loading previous spots file. Starting fresh.")
            spots = {}
        except Exception as e:
            print(f"Error loading spots from {config.SPOTS_FILE}: {e}")
            speak("Could not load spots.")
            spots = {}
    else:
        print("Spots file not found. Starting with empty spots.")
        spots = {}

def reset_spots():
    """Delete all spots"""
    global spots
    spots = {}
    if os.path.exists(config.SPOTS_FILE):
        try:
            os.remove(config.SPOTS_FILE)
            speak("All spots reset.")
        except Exception as e:
            print(f"Error removing spots file {config.SPOTS_FILE}: {e}")
            speak("Error resetting spots.")
    else:
        speak("No spots to reset.")

def add_spot(name):
    """Add a new spot at current cursor position"""
    if name in spots:
        speak(f"Name {name} is already used.")
        return False
    if name in config.protected_names:
        speak(f"Cannot use protected name {name}")
        return False

    position = pyautogui.position()
    spots[name] = position
    save_spots()
    speak(f"Marked spot {name}")
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
        pyautogui.moveTo(x, y, duration=0.25)
        show_label(name, x, y)
        return True
    else:
        speak(f"No spot named {name}")
        return False

def list_spots():
    """List all saved spots"""
    if spots:
        speak("Spots: " + ", ".join(spots.keys()))
    else:
        speak("No spots saved.")
    return spots

def get_spots():
    """Return the spots dictionary"""
    return spots

# Load spots when the module is imported
load_spots()
