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
from scipy.signal import resample
import webrtcvad

# Global variable to keep the whisper model loaded
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("--- Loading Local Whisper Model (tiny) ---")
        _whisper_model = whisper.load_model("tiny")
        print("--- Model Loaded ---")
    return _whisper_model

def find_external_mic():
    """Finds the index of the external microphone (RØDE VideoMic GO II)."""
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if "RØDE" in dev['name'] or "VideoMic" in dev['name']:
            return i
    return None

def speak(text, stop_callback=None):
    """
    Converts text to speech and plays it back.
    If stop_callback is provided and returns True, playback stops.
    Returns the text if interrupted, else None.
    """
    if not text:
        return None
        
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
        
        interrupted = False
        while pygame.mixer.music.get_busy():
            if stop_callback and stop_callback():
                pygame.mixer.music.stop()
                interrupted = True
                break
            time.sleep(0.05)
            
        pygame.mixer.quit()
        if os.path.exists(path):
            os.remove(path)
        
        return text if interrupted else None
    except Exception as e:
        print(f"Error in TTS: {e}")
        return None

def resample_audio(audio_data, original_sr, target_sr):
    """Resamples audio data to the target sample rate."""
    if original_sr == target_sr:
        return audio_data.astype(np.int16)
    number_of_samples = round(len(audio_data) * float(target_sr) / original_sr)
    resampled_audio = resample(audio_data, number_of_samples)
    return resampled_audio.astype(np.int16)

def listen_with_vad(timeout=20, silence_limit=0.8):
    """
    Listens using VAD. Optimized for quick response after silence.
    """
    device_index = find_external_mic()
    mic_info = sd.query_devices(device_index)
    native_fs = int(mic_info['default_samplerate'])
    target_fs = 16000
    
    vad_frame_ms = 30
    native_frame_size = int(native_fs * vad_frame_ms / 1000)
    
    vad = webrtcvad.Vad(3) # Maximum aggressiveness for sharp silence detection
    
    audio_buffer = [] 
    speaking = False
    silence_start = None
    start_time = time.time()
    
    print(f"--- Listening (VAD Active, Mic SR: {native_fs})... ---")
    
    try:
        with sd.InputStream(samplerate=native_fs, blocksize=native_frame_size, device=device_index, dtype='int16', channels=1) as stream:
            while True:
                frame, overflowed = stream.read(native_frame_size)
                if time.time() - start_time > timeout:
                    print("--- Listening timeout reached ---")
                    break
                
                # Resample for VAD
                vad_frame = resample_audio(frame.flatten(), native_fs, target_fs)
                
                # VAD check
                try:
                    is_speech = vad.is_speech(vad_frame.tobytes(), target_fs)
                except Exception as ve:
                    print(f"VAD Frame Error: {ve}")
                    is_speech = False
                
                if is_speech:
                    if not speaking:
                        print("--- Speech Detected! ---")
                    speaking = True
                    silence_start = None
                
                if speaking:
                    audio_buffer.append(frame.copy())
                    if not is_speech:
                        if silence_start is None:
                            silence_start = time.time()
                        # If silent for more than silence_limit, stop immediately
                        if time.time() - silence_start > silence_limit:
                            print(f"--- Silence threshold ({silence_limit}s) met. Stopping... ---")
                            break
                
                # If hasn't started speaking in 7 seconds, exit
                if not speaking and time.time() - start_time > 7.0:
                    print("--- No speech detected in initial 7s ---")
                    break

        if not audio_buffer:
            return "Newton heard only silence."

        print(f"--- Processing {len(audio_buffer)} frames of audio... ---")
        audio_data = np.concatenate(audio_buffer)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            wav.write(temp_path, native_fs, audio_data)
            
        model = get_whisper_model()
        result = model.transcribe(temp_path, fp16=False, language='en')
        text = result["text"].strip()
        
        print(f"--- Transcription: {text} ---")
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return text
    except Exception as e:
        print(f"--- Voice Engine Error: {e} ---")
        return f"Error: {e}"

def is_user_speaking():
    """Quick check for interruption."""
    device_index = find_external_mic()
    mic_info = sd.query_devices(device_index)
    native_fs = int(mic_info['default_samplerate'])
    target_fs = 16000
    vad_frame_ms = 30
    native_frame_size = int(native_fs * vad_frame_ms / 1000)
    
    vad = webrtcvad.Vad(2)
    
    try:
        with sd.InputStream(samplerate=native_fs, blocksize=native_frame_size, device=device_index, dtype='int16', channels=1) as stream:
            speech_count = 0
            for _ in range(5):
                frame, _ = stream.read(native_frame_size)
                vad_frame = resample_audio(frame.flatten(), native_fs, target_fs)
                if vad.is_speech(vad_frame.tobytes(), target_fs):
                    speech_count += 1
            return speech_count >= 3
    except:
        return False

def listen():
    return listen_with_vad()
