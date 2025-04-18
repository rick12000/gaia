"""UI-related functionality for GAIA"""

import tkinter as tk
import pyautogui
import threading
import queue
from speech import speak
import config
from time import sleep

# Globals
ui_action_queue = queue.Queue()  # Queue for UI operations to run on main thread
root = None  # Main Tkinter root window
visualization_window = None
visualization_active = False

def initialize_ui():
    """Initialize the UI system"""
    global root
    
    # Initialize tkinter root window for the main thread
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Start processing UI actions
    process_ui_queue()
    
    return root

def process_ui_queue():
    """Process pending UI actions on the main thread"""
    try:
        while not ui_action_queue.empty():
            action, args = ui_action_queue.get_nowait()
            
            if action == "show_label":
                _show_label_impl(*args)
            elif action == "visualize_marks":
                _visualize_spots_impl(*args)
            elif action == "close_visualization":
                if visualization_window:
                    visualization_window.destroy()
                    visualization_active = False
            elif action == "confirmation_dialog":
                _show_confirmation_dialog(*args)
    except Exception as e:
        print(f"Error processing UI action: {e}")
    
    # Schedule to run again after 100ms
    if root:
        root.after(100, process_ui_queue)

def show_label(name, x, y):
    """Queue a label to be shown on the main thread"""
    ui_action_queue.put(("show_label", (name, x, y)))

def _show_label_impl(name, x, y):
    """Implementation of show_label that runs on the main thread"""
    global root
    if not root:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.config(bg="black")
        root.wm_attributes("-transparentcolor", "black")
    label = tk.Label(root, text=f"📍 {name}", fg="white", bg="black", font=("Arial", 12, "bold"))
    label.place(x=x+10, y=y+10)
    label.update()
    if config.LABEL_DURATION > 0:
        label.after(config.LABEL_DURATION, label.destroy)

def visualize_spots(spots):
    """Queue visualization to be shown on the main thread"""
    ui_action_queue.put(("visualize_marks", (spots,)))
    return True

def _visualize_spots_impl(spots):
    """Implementation of visualize_spots that runs on the main thread"""
    global visualization_window, visualization_active
    
    # Close existing visualization if any
    if visualization_window:
        try:
            visualization_window.destroy()
        except:
            pass
        visualization_window = None
    
    if not spots:
        speak("No spots to visualize.")
        return
    
    # Define closing function
    def close_visualization():
        global visualization_window, visualization_active
        if visualization_window:
            visualization_window.destroy()
            visualization_window = None
            visualization_active = False
    
    try:
        # Create new visualization window
        visualization_window = tk.Toplevel()  # Use Toplevel instead of Tk for additional windows
        visualization_window.title("GAIA Spot Visualization")
        visualization_window.attributes("-alpha", 0.8)  # Semi-transparent
        visualization_window.attributes("-topmost", True)
        
        # Make window fullscreen and transparent for clicks
        screen_width, screen_height = pyautogui.size()
        visualization_window.geometry(f"{screen_width}x{screen_height}+0+0")
        visualization_window.overrideredirect(True)  # Borderless
        visualization_window.config(bg="#333333")
        
        # Add a label explaining how to close
        info_label = tk.Label(visualization_window, 
                             text="GAIA Mark Visualization (say 'escape' to close)",
                             fg="white", bg="#333333", font=("Arial", 14))
        info_label.pack(pady=10)
        
        # Canvas to draw spots
        canvas = tk.Canvas(visualization_window, bg="#333333", 
                          width=screen_width, height=screen_height,
                          highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw spots
        for name, position in spots.items():
            x, y = position
            # Draw a circle at spot
            circle_radius = 10
            canvas.create_oval(x-circle_radius, y-circle_radius, 
                              x+circle_radius, y+circle_radius, 
                              fill="red", outline="white", width=2)
            # Add name label
            canvas.create_text(x, y-circle_radius-5, text=name, fill="white",
                              font=("Arial", 12), anchor=tk.S)
        
        visualization_active = True
        
        # Make the window capture the escape key to close
        visualization_window.bind('<Escape>', lambda e: close_visualization())
        
        # Auto-close after 10 seconds
        visualization_window.after(10000, close_visualization)
        
        # Focus on the window
        visualization_window.focus_set()
        
        print("Visualization window created successfully")
    except Exception as e:
        print(f"Error creating visualization window: {e}")
        speak("Error showing marks visualization.")

def _show_confirmation_dialog(message, callback, timeout=config.CLOSE_CONFIRMATION_TIMEOUT):
    """Show a confirmation dialog that closes after a timeout"""
    dialog = tk.Toplevel()
    dialog.title("Confirmation")
    dialog.attributes("-topmost", True)
    dialog.geometry("400x150")
    
    # Center the dialog on screen
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # Dialog content
    tk.Label(dialog, text=message, font=("Arial", 12)).pack(pady=20)
    tk.Label(dialog, text=f"Say 'yes' to confirm or 'no' to cancel.", font=("Arial", 10)).pack()
    
    # Set up timer with countdown
    countdown_label = tk.Label(dialog, text=f"Waiting for {timeout} seconds...", font=("Arial", 10))
    countdown_label.pack(pady=10)
    
    confirmation_received = [False]  # Use list for mutable state
    
    def update_countdown(seconds_left):
        if seconds_left <= 0 or not dialog.winfo_exists():
            if not confirmation_received[0]:
                # Time's up and no confirmation, cancel the operation
                try:
                    dialog.destroy()
                except:
                    pass
                callback(False)
            return
        
        countdown_label.config(text=f"Waiting for {seconds_left} seconds...")
        dialog.after(1000, update_countdown, seconds_left - 1)
    
    # Start the countdown
    update_countdown(timeout)
    
    # Return the dialog and confirmation state for later handling
    return dialog, confirmation_received

def show_confirmation_dialog(message, callback):
    """Show a confirmation dialog with timeout"""
    ui_action_queue.put(("confirmation_dialog", (message, callback)))

def shutdown_ui():
    """Clean up UI resources"""
    global root
    if root and root.winfo_exists():
        root.destroy()

def visualize_spots(spots_dict, duration=3, adjust_for_titlebar=False):
    """
    Visualize all spots on screen temporarily
    
    Args:
        spots_dict: Dictionary of spot names and coordinates
        duration: How long to show the spots (seconds)
        adjust_for_titlebar: Whether to adjust for titlebar offset
    """
    if not spots_dict:
        return
        
    # Create a fullscreen transparent window
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.7)
    root.attributes("-fullscreen", True)
    
    # Measure screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate title bar offset (typically around 30 pixels but can vary)
    titlebar_offset = 30 if adjust_for_titlebar else 0
    
    # Create a canvas that covers the screen
    canvas = tk.Canvas(root, width=screen_width, height=screen_height, 
                      bg="black", highlightthickness=0)
    canvas.pack()
    
    # Draw each spot with its name
    for name, (x, y) in spots_dict.items():
        # Adjust y position to account for title bar if needed
        adjusted_y = y - titlebar_offset if adjust_for_titlebar else y
        
        # Create a distinctive marker (red circle with white outline)
        circle_size = 15
        canvas.create_oval(x-circle_size, adjusted_y-circle_size, 
                          x+circle_size, adjusted_y+circle_size, 
                          fill="red", outline="white", width=2)
        
        # Add spot name as text
        canvas.create_text(x, adjusted_y-25, text=name, fill="white", 
                          font=("Arial", 12, "bold"))
    
    # Update the display
    root.update()
    
    # Keep window open for duration
    sleep(duration)
    
    # Clean up
    root.destroy()
