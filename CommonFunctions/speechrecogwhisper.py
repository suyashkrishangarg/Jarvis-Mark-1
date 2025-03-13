import speech_recognition as sr
import os
import numpy as np
from faster_whisper import WhisperModel, BatchedInferencePipeline
import colorama

colorama.init(autoreset=True)

# Load the model once.
model = WhisperModel('tiny', device="cpu", compute_type="int8")
batched_model = BatchedInferencePipeline(model=model)

print("==> Speech Recognition Loaded!")

# Create a single recognizer instance.
r = sr.Recognizer()

# Optionally, pre-adjust for ambient noise.
with sr.Microphone(sample_rate=16000) as source:
    r.adjust_for_ambient_noise(source)

def speechrecognition(Print=True, Translate=False):
    query = ''
    # Use a specific sample rate to match model expectations.
    with sr.Microphone(sample_rate=16000) as source:
        if Print:
            print(colorama.Fore.MAGENTA + "\nListening...")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=0)  # Adjust the timeout as needed

    try:
        if Print:
            print(colorama.Fore.GREEN + "==> You Said: ", end="")
        
        # Convert audio raw data directly to a numpy array (normalized to -1.0 to 1.0)
        audio_np = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe directly from the in-memory numpy array.
        segments, _ = batched_model.transcribe(
            audio_np,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            language='en'
        )
        for segment in segments:
            text = segment.text.lstrip()
            if Print:
                print(colorama.Fore.LIGHTGREEN_EX + text, end="", flush=True)
            query += text

        print()
        return query.lower()
    
    except Exception as e:
        if Print:
            print("Error during transcription:", e)
        return ""

if __name__=="__main__":
    while True:
        speechrecognition()