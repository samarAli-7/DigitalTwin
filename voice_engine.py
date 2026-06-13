import asyncio
import edge_tts
import pygame
import os
import time
import tempfile
import whisper
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav

# Global variable to keep the whisper model loaded
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("--- Loading Local Whisper Model (tiny) ---")
        _whisper_model = whisper.load_model("tiny")
        print("--- Model Loaded ---")
    return _whisper_model

def speak(text):
    """
    Converts text to speech using edge-tts (neural voices) and plays it back.
    """
    if not text:
        return
        
    try:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        voice = "en-GB-ThomasNeural"
        
        async def generate_tts():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(path)

        asyncio.run(generate_tts())
        
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error in TTS: {e}")

def find_external_mic():
    """Finds the index of the external microphone (RØDE VideoMic GO II)."""
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if "RØDE" in dev['name'] or "VideoMic" in dev['name']:
            print(f"--- Using External Mic: {dev['name']} (Index {i}) ---")
            return i
    return None

def listen():
    """
    Listens using sounddevice for more direct microphone access and transcribes with Whisper.
    """
    duration = 5  # Listen for 5 seconds
    fs = 48000    # Sample rate (Matched to RØDE VideoMic GO II)
    device_index = find_external_mic()
    
    try:
        print(f"--- Listening for {duration} seconds... ---")
        # Record audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=device_index)
        sd.wait()  # Wait until recording is finished
        print("--- Recording complete. Processing... ---")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            wav.write(temp_path, fs, recording)
            
        # Transcribe
        model = get_whisper_model()
        result = model.transcribe(temp_path, fp16=False)
        text = result["text"].strip()
        
        print(f"--- Transcription: '{text}' ---")
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return text if text else "Newton heard only silence."

    except Exception as e:
        print(f"--- Audio Capture Error: {e} ---")
        return f"Newton's ears have failed him: {e}"
