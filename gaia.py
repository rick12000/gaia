"""
GAIA - Generalized Audio Interface Assistant
A voice control system for computer interaction.
"""

import os
import time
import sounddevice as sd
import threading
import json
import queue
import pyautogui
import pyperclip

# Import from other modules
import config
from speech import (
    initialize_speech, speak, audio_callback, initialize_recognizer, get_audio_queue
)
from ui_manager import initialize_ui
from spot_manager import load_spots
# Import command_handler module itself to access its state directly
import command_handler
# Explicitly import functions needed
from command_handler import handle_command, stop_dictation_mode

# Define the paste interval here (or load from config if preferred)
DICTATION_PASTE_INTERVAL = 1.5 # Seconds

def main():
    """Main entry point for GAIA"""

    # Check for the speech recognition model
    if not os.path.exists(config.MODEL_PATH):
        print(f"Download a Vosk model and extract it to: {config.MODEL_PATH}")
        return
        
    # Initialize speech synthesis
    initialize_speech()
    
    # Initialize the speech recognition
    recognizer = initialize_recognizer()
    
    # Load saved spots
    load_spots()
    
    # Initialize UI system
    root = initialize_ui()

    # Wait a moment for speech thread to initialize
    time.sleep(1)
    
    # Start the audio stream
    with sd.RawInputStream(
        samplerate=16000, 
        blocksize=config.BLOCK_SIZE, 
        dtype='int16',
        channels=1, 
        callback=audio_callback
    ):
        speak("Voice control activated.")

        # Start main loop
        try:
            # Update tkinter root occasionally to process events and audio
            def update_tk_and_process_audio():
                # Process tkinter events
                root.update_idletasks()
                root.update()

                now = time.time() # Get current time once per update cycle

                # --- Dictation Mode Logic ---
                if command_handler.is_dictating:
                    # Check timeouts first
                    if now - command_handler.dictation_start_time > command_handler.DICTATION_MAX_DURATION:
                        print("Dictation stopped due to max duration timeout.")
                        stop_dictation_mode(reason="timeout_max_duration")
                        # Schedule next check and return
                        root.after(10, update_tk_and_process_audio)
                        return
                    # Check inactivity timeout based on last speech time
                    if command_handler.last_speech_time > 0 and now - command_handler.last_speech_time > command_handler.DICTATION_INACTIVITY_TIMEOUT:
                        print("Dictation stopped due to inactivity timeout.")
                        stop_dictation_mode(reason="timeout_inactivity")
                        # Schedule next check and return
                        root.after(10, update_tk_and_process_audio)
                        return

                    # Process audio for dictation
                    try:
                        audio_queue = get_audio_queue()
                        data = audio_queue.get_nowait()
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            if "text" in result and result["text"]:
                                recognized_text = result["text"].strip()
                                print(f"Dictation heard: '{recognized_text}'")
                                command_handler.last_speech_time = now # Update last speech time

                                if recognized_text.lower() == "stop dictation":
                                    stop_dictation_mode(reason="command")
                                    # Don't process further this cycle if stopped
                                    root.after(10, update_tk_and_process_audio)
                                    return
                                else:
                                    words = recognized_text.split()
                                    if words:
                                        command_handler.dictation_word_chunk.extend(words)
                                        # No immediate pasting here, handled by time check below

                    except queue.Empty:
                        pass # No new audio data

                    # --- Time-based Pasting Logic ---
                    # Check if there are words and enough time has passed since the last activity (speech or paste)
                    if command_handler.dictation_word_chunk and \
                       (now - max(command_handler.last_speech_time, command_handler.last_paste_time) > DICTATION_PASTE_INTERVAL):

                        chunk_to_paste = " ".join(command_handler.dictation_word_chunk)
                        command_handler.dictation_word_chunk = [] # Clear chunk *after* copying

                        try:
                            # Copy only the words, no trailing space yet
                            pyperclip.copy(chunk_to_paste)
                            # Paste the words
                            pyautogui.hotkey('ctrl', 'v')
                            # Wait briefly for paste to complete
                            time.sleep(0.05)
                            # Explicitly type a space after the pasted chunk
                            pyautogui.press('space')
                            print(f"Pasted chunk: '{chunk_to_paste}' + space")
                            command_handler.last_paste_time = now # Update last paste time
                            # Optional small delay after space
                            time.sleep(0.05)
                        except Exception as paste_err:
                            print(f"Error pasting dictation chunk: {paste_err}")
                            # If paste fails, consider putting words back? For now, they are lost.
                            # command_handler.dictation_word_chunk = chunk_to_paste.split() # Option to restore

                    # Schedule the next update regardless of pasting
                    root.after(10, update_tk_and_process_audio)
                    return # End dictation processing for this cycle

                # --- Regular Command Processing (Not Dictating) ---
                try:
                    audio_queue = get_audio_queue()
                    data = audio_queue.get_nowait()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if "text" in result and result["text"]:
                            command_text = result["text"]
                            threading.Thread(
                                target=handle_command,
                                args=(command_text,),
                                daemon=True
                            ).start()
                except queue.Empty:
                    pass

                # Schedule the next update
                root.after(10, update_tk_and_process_audio)

            # Start the update loop
            update_tk_and_process_audio()
            
            # Start tkinter main loop
            root.mainloop()
            
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            from ui_manager import shutdown_ui
            from speech import shutdown_speech
            
            shutdown_speech()
            shutdown_ui()

if __name__ == "__main__":
    main()
