"""Speech recognition and TTS functionality"""

import queue
import threading
import pyttsx3
from vosk import Model, KaldiRecognizer

import config

# Globals
audio_queue = queue.Queue()
speech_queue = queue.Queue()  # Queue for text to be spoken
speech_thread = None
speech_running = False
engine = None  # Will be initialized in speech worker thread

def initialize_speech():
    """Start the speech worker thread"""
    global speech_thread, speech_running
    
    speech_running = True
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()

def speak(text):
    """Queue text to be spoken"""
    speech_queue.put(text)
    print(f"Queued speech: '{text}'")

def speech_worker():
    """Dedicated thread for speech synthesis"""
    global engine, speech_running
    
    # Initialize TTS engine in this thread
    try:
        engine = pyttsx3.init()
        
        # Set voice gender preference - improved selection
        voices = engine.getProperty('voices')
        selected_voice = None
        
        # Better voice selection logic
        if config.VOICE_GENDER.lower() == "male":
            # Try to find a voice with "male" in the name or ID
            for voice in voices:
                if "male" in voice.name.lower() or "david" in voice.name.lower() or "mark" in voice.name.lower():
                    selected_voice = voice.id
                    break
            # If no specific male voice found, use the first voice (usually male)
            if selected_voice is None and voices:
                selected_voice = voices[0].id
        else:  # female
            # Try to find a voice with "female" in the name or common female voice names
            for voice in voices:
                if ("female" in voice.name.lower() or "zira" in voice.name.lower() 
                    or "elsa" in voice.name.lower() or "helen" in voice.name.lower()):
                    selected_voice = voice.id
                    break
            # If no specific female voice found, use the second voice if available (often female)
            if selected_voice is None and len(voices) > 1:
                selected_voice = voices[1].id
            # Last resort, use any available voice
            elif selected_voice is None and voices:
                selected_voice = voices[0].id
        
        # If we found a voice, set it
        if selected_voice:
            engine.setProperty('voice', selected_voice)
            print(f"Selected voice: {selected_voice}")
            
        # Set speech rate (speed)
        engine.setProperty('rate', engine.getProperty('rate') * config.SPEECH_RATE)
        
        # Set speech volume
        current_volume = engine.getProperty('volume')
        engine.setProperty('volume', min(1.0, current_volume * config.SPEECH_VOLUME))  # Ensure it doesn't exceed 1.0
        
        print(f"TTS Engine initialized with {config.VOICE_GENDER} voice at {config.SPEECH_RATE}x speed and {config.SPEECH_VOLUME}x volume")
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return
    
    speech_running = True
    
    while speech_running:
        try:
            # Get text to speak with timeout to check speech_running periodically
            text = speech_queue.get(timeout=0.5)
            print(f"Speaking: '{text}'")
            
            # Process the speech
            engine.say(text)
            engine.runAndWait()
            
            # Mark task as done
            speech_queue.task_done()
            
        except queue.Empty:
            # No speech to process, continue waiting
            continue
        except Exception as e:
            print(f"Error in speech worker: {e}")

def shutdown_speech():
    """Clean up speech resources"""
    global speech_running
    speech_running = False
    if speech_thread:
        speech_thread.join(timeout=1.0)

def initialize_recognizer():
    """Initialize the speech recognition model"""
    model = Model(config.MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)
    return recognizer

def audio_callback(indata, frames, time, status):
    """Callback for audio stream data"""
    if status:
        print(status)
    audio_queue.put(bytes(indata))

def get_audio_queue():
    """Access to the audio queue"""
    return audio_queue
