"""Configuration settings for GAIA"""

import sys
import os
from appdirs import user_data_dir

# --- Application Info ---
APP_NAME = "GAIA"
APP_AUTHOR = "YourNameOrOrg"  # Used by appdirs

# --- Path Configuration ---
def get_base_path():
    """ Get the base path for resources, handling PyInstaller bundling. """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle (frozen)
        return sys._MEIPASS
    else:
        # Running as a normal script
        # Assumes config.py is in src/, and resources are relative to the parent dir
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

BASE_PATH = get_base_path()

# --- Vosk Model ---
# Expect the model dir to be bundled at the root, or exist alongside src/
MODEL_DIR_NAME = "vosk-model-small-en-us-0.15"
MODEL_PATH = os.path.join(BASE_PATH, MODEL_DIR_NAME)
BLOCK_SIZE = 4000  # Reduced for better responsiveness

# --- User Data ---
# Use a standard user data directory for spots.json
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)  # Create the directory if it doesn't exist
SPOTS_FILE = os.path.join(USER_DATA_DIR, "spots.json")

# --- Speech Settings ---
VOICE_GENDER = "female"  # "male" or "female"
SPEECH_RATE = 1.0  # Multiplier for default speech rate (e.g., 1.0 is normal, 1.5 is faster)
SPEECH_VOLUME = 1.0  # Multiplier for default volume (0.0 to 1.0+)

# --- UI Settings ---
LABEL_DURATION_MS = 2000  # How long labels stay on screen in milliseconds

# Add protected names for spots that can't be used as they conflict with commands
protected_names = [
    "stop", "exit", "quit", "mark", "unmark", 
    "go", "list", "reset", "visualize", 
    "click", "double", "spots", "marks"
]

# --- Input Settings ---
INPUT_TIMEOUT_SECONDS = 5  # Timeout for waiting for voice commands

# Key press speed settings
KEY_PRESS_INTERVAL = 0.1  # Base interval between key presses in seconds
KEY_RELEASE_INTERVAL = 0.05  # Base interval between release and next press
KEY_SPEED_MULTIPLIER = 1.0  # Current speed multiplier (adjusted by faster/slower)
SPEED_INCREMENT = 2.0  # Increased for more noticeable changes
MIN_SPEED_MULTIPLIER = 0.05  # Allow very slow speeds (1 keypress every ~5 seconds)
PAGE_KEY_PRESS_INTERVAL = 0.5  # Slower base interval for page up/down (seconds)
PAGE_KEY_RELEASE_INTERVAL = 0.5  # Slower base interval for release

# Window management
CLOSE_CONFIRMATION_TIMEOUT = 5  # Seconds to wait for confirmation before canceling

print(f"Base path: {BASE_PATH}")
print(f"Model path: {MODEL_PATH}")
print(f"Spots file path: {SPOTS_FILE}")
