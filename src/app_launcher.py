"""Application and website launcher for GAIA"""

import subprocess
import os
from speech import speak

# Dictionary of websites
common_websites = {
    "youtube": "https://www.youtube.com",
    "you tube": "https://www.youtube.com",  # Common variation
    "google": "https://www.google.com",
    "github": "https://github.com",
    "stack overflow": "https://stackoverflow.com",
    "stackoverflow": "https://stackoverflow.com",  # Normalized variation
    "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",  # Common variation
    "maps": "https://www.google.com/maps",
    "google maps": "https://www.google.com/maps"  # Common variation
}

# Dictionary of applications
common_apps = {
    "chrome": {
        "windows": ["start", "chrome"],
        "paths": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
    },
    "vs": {  # Changed from "vs code" to "vs"
        "windows": ["start", "code"],
        "paths": [
            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "C:\\Users\\ricca\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
        ]
    },
    "notepad": {
        "windows": ["start", "notepad"],
        "paths": ["C:\\Windows\\System32\\notepad.exe"]
    },
    "explorer": {
        "windows": ["start", "explorer"],
        "paths": ["C:\\Windows\\explorer.exe"]
    },
    "obsidian": {
        "windows": ["start", "obsidian"],
        "paths": [
            "C:\\Users\\ricca\\AppData\\Local\\Obsidian\\Obsidian.exe"
        ]
    }
}

def open_application(app_name):
    """Open an application"""
    app_info = common_apps.get(app_name.lower())
    if not app_info:
        return False
    
    # Method 1: Try using Windows "start" command
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(app_info["windows"], shell=True)
            print(f"Opened {app_name} using Windows start command")
            return True
    except Exception as e:
        print(f"Failed to start {app_name} with start command: {e}")
    
    # Method 2: Try direct paths
    for path in app_info["paths"]:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                print(f"Opened {app_name} using direct path: {path}")
                return True
            except Exception as e:
                print(f"Failed to start {app_name} with path {path}: {e}")
    
    # Method 3: Last resort, try the app name directly
    try:
        subprocess.Popen(app_name.lower())
        print(f"Opened {app_name} using app name directly")
        return True
    except Exception:
        pass
        
    return False

def open_website(site_name):
    """Open a website by name"""
    import webbrowser
    
    # Try direct match first
    if site_name in common_websites:
        url = common_websites[site_name]
    else:
        # Try normalized match (remove spaces)
        normalized_name = site_name.replace(" ", "")
        for k, v in common_websites.items():
            if k.replace(" ", "") == normalized_name:
                url = v
                break
        else:  # No match found
            return False
    
    try:
        webbrowser.open(url)
        print(f"Opening website: {url}")
        return True
    except Exception as e:
        print(f"Error opening website: {e}")
        return False

def go_to_target(target):
    """Open a website or application"""
    # First check if it's a website
    if open_website(target):
        return True
    
    # Then check if it's an application
    if target in common_apps:
        if open_application(target):
            return True
        else:
            speak(f"Failed to launch {target}")
            return False
    
    speak(f"I don't know how to open {target}")
    return False
