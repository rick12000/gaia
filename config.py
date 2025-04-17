"""Configuration settings for GAIA"""

# Speech recognition
MODEL_PATH = "vosk-model-small-en-us-0.15"
BLOCK_SIZE = 4000  # Reduced for better responsiveness

# Voice preferences
VOICE_GENDER = "male"  # Options: "male" or "female"
SPEECH_RATE = 0.9  # Lowered from 1.2 for slower speech (1.0 is normal speed)
SPEECH_VOLUME = 1.5  # Volume multiplier (1.0 is default, higher values increase volume)

# UI settings
SPOTS_FILE = "spots.json"
LABEL_DURATION = 3000  # milliseconds (set to 0 for permanent labels)

# Add protected names for spots that can't be used as they conflict with commands
protected_names = [
    "stop", "exit", "quit", "mark", "unmark", 
    "go", "list", "reset", "visualize", 
    "click", "double", "spots", "marks"
]

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
