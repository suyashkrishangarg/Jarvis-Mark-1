import numpy as np
import threading
import sounddevice as sd
import queue
import sys
import os
import pygame
from kokoro import KPipeline
from time import time as t, sleep
import typing

# Add current directory to path
current_dir = os.getcwd()
sys.path.append(current_dir)
from API_keys import AI_Name

# Global flags using threading.Event for thread safety.
STOP_SPEECH_EVENT = threading.Event()
HOT_WORD_DECT_IS_ON_EVENT = threading.Event()
# Add a new event to control text processing
STOP_TEXT_PROCESSING_EVENT = threading.Event()

# Fast, thread-safe audio buffer.
global_buffer = queue.Queue(maxsize=2000000)

# Initialize Kokoro TTS pipeline once for efficiency.
pipeline = KPipeline(lang_code='a')

# Persistent low-latency audio stream.
def audio_callback(outdata, frames, time_info, status):
    """Streams buffered audio to output device with minimal delay."""
    samples = []
    try:
        for _ in range(frames):
            if STOP_SPEECH_EVENT.is_set():
                outdata.fill(0)
                return
            samples.append(global_buffer.get_nowait())
        outdata[:] = np.array(samples, dtype=np.float32).reshape(outdata.shape)
    except queue.Empty:
        outdata.fill(0)

stream = sd.OutputStream(
    samplerate=24000,
    channels=1,
    callback=audio_callback
)
stream.start()

def text_chunker(chunks: typing.Iterator[str]) -> typing.Iterator[str]:
    """
    Improved text chunker that accumulates text until it forms a meaningful 
    speech segment before yielding. This prevents choppy speech when receiving 
    small text chunks.
    """
    splitters = (".", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", "\n")
    buffer = ""
    
    for text in chunks:
        buffer += text
        
        # Find the last occurrence of any splitter
        last_splitter_pos = -1
        for splitter in splitters:
            pos = buffer.rfind(splitter)
            if pos > last_splitter_pos:
                last_splitter_pos = pos
        
        # If we have a substantial chunk ending with a splitter, yield it
        if last_splitter_pos > 0:
            chunk_to_yield = buffer[:last_splitter_pos+1]
            # Add a space if it doesn't end with whitespace
            if not chunk_to_yield.endswith((" ", "\n")):
                chunk_to_yield += " "
            yield chunk_to_yield
            buffer = buffer[last_splitter_pos+1:]
    
    # Don't forget any remaining text
    if buffer:
        if not buffer.endswith((" ", "\n")):
            buffer += " "
        yield buffer

def generate_audio(text: str):
    """Generates audio from text and streams it in real-time."""
    if not text or text.isspace():
        return
        
    STOP_SPEECH_EVENT.clear()
    generator = pipeline(text, voice='af_heart', speed=1.25)
    prefill_samples = 40000
    count = 0

    for i, (gs, ps, audio) in enumerate(generator):
        if STOP_SPEECH_EVENT.is_set() or STOP_TEXT_PROCESSING_EVENT.is_set():
            break
        # Convert tensor efficiently.
        audio_np = audio.cpu().numpy().ravel()

        # Batch enqueue samples for speed.
        for sample in audio_np:
            if STOP_SPEECH_EVENT.is_set() or STOP_TEXT_PROCESSING_EVENT.is_set():
                break
            global_buffer.put(sample, block=True)
            count += 1

        if count >= prefill_samples:
            pass

def stop_speech():
    STOP_SPEECH_EVENT.set()
    # Also stop text processing
    STOP_TEXT_PROCESSING_EVENT.set()
    # Clear the global audio buffer.
    try:
        while True:
            global_buffer.get_nowait()
    except queue.Empty:
        pass
    # Clear the text queue to prevent further processing
    try:
        while True:
            text_queue.get_nowait()
            text_queue.task_done()
    except queue.Empty:
        pass
    pygame.mixer.quit()

def detect_clap(indata, frames, time, status):
    """Detects if a clap is made using a volume threshold."""
    if not HOT_WORD_DECT_IS_ON_EVENT.is_set():
        return
    volume_norm = np.linalg.norm(indata) * 10
    # You may want to lower this threshold if your claps are not registering.
    if volume_norm > 40:
        # print(f"\nClap detected with volume_norm: {volume_norm}")
        stop_speech()

def clap_detection():
    """Monitors for claps and stops speech if detected."""
    with sd.InputStream(callback=detect_clap):
        while HOT_WORD_DECT_IS_ON_EVENT.is_set():
            sd.sleep(100)

# Global text queue for TTS chunks.
text_queue = queue.Queue()

def tts_worker():
    """
    Worker thread that processes text chunks.
    Now with improved handling for smaller chunks of text.
    """
    accumulated_text = []
    
    while not STOP_TEXT_PROCESSING_EVENT.is_set():
        try:
            # Wait for a new chunk.
            chunk = text_queue.get(timeout=0.1)
        except queue.Empty:
            # If we have accumulated text and no new chunks for a while, process it
            if accumulated_text and not STOP_TEXT_PROCESSING_EVENT.is_set():
                complete_text = "".join(accumulated_text)
                for speech_segment in text_chunker([complete_text]):
                    if STOP_TEXT_PROCESSING_EVENT.is_set():
                        break
                    generate_audio(speech_segment)
                accumulated_text = []
            continue

        if chunk is None:
            # Process any remaining accumulated text
            if accumulated_text and not STOP_TEXT_PROCESSING_EVENT.is_set():
                complete_text = "".join(accumulated_text)
                for speech_segment in text_chunker([complete_text]):
                    if STOP_TEXT_PROCESSING_EVENT.is_set():
                        break
                    generate_audio(speech_segment)
            text_queue.task_done()
            break
        
        if not chunk:
            text_queue.task_done()
            continue
            
        # Check if we should stop processing
        if STOP_TEXT_PROCESSING_EVENT.is_set():
            text_queue.task_done()
            continue
            
        # Accumulate the text instead of processing immediately
        accumulated_text.append(chunk)
        
        # Check if we have a complete sentence or enough content to speak
        complete_text = "".join(accumulated_text)
        
        # If we have a substantial chunk ending with sentence terminators, process it
        if any(complete_text.endswith(term) for term in [".", "!", "?", "\n"]) and not STOP_TEXT_PROCESSING_EVENT.is_set():
            for speech_segment in text_chunker([complete_text]):
                if STOP_TEXT_PROCESSING_EVENT.is_set():
                    break
                generate_audio(speech_segment)
            accumulated_text = []
        
        text_queue.task_done()

def text_stream():
    """Example text stream yielding multiple chunks (emojis will be removed)."""
    # Test with single words
    yield "This "
    yield "is "
    yield "a "
    yield "test "
    yield "with "
    yield "single "
    yield "words. "
    
    # Test with a full sentence
    yield "Line one: This is a default line of text for TTS.\n"
    
    # Test with partial sentences
    yield "Line two: The quick "
    yield "brown fox jumps "
    yield "over the lazy dog.\n"
    
    yield "Line three: Kokoro TTS is generating speech from text."
    sleep(2)
    yield "This "
    yield "is "
    yield "a "
    yield "test "
    yield "with "
    yield "single "
    yield "words. "
    
    # Test with a full sentence
    yield "Line one: This is a default line of text for TTS.\n"
    
    # Test with partial sentences
    yield "Line two: The quick "
    yield "brown fox jumps "
    yield "over the lazy dog.\n"
    
    yield "Line three: Kokoro TTS is generating speech from text."
    sleep(2)
    yield "This "
    yield "is "
    yield "a "
    yield "test "
    yield "with "
    yield "single "
    yield "words. "
    
    # Test with a full sentence
    yield "Line one: This is a default line of text for TTS.\n"
    
    # Test with partial sentences
    yield "Line two: The quick "
    yield "brown fox jumps "
    yield "over the lazy dog.\n"
    
    yield "Line three: Kokoro TTS is generating speech from text."
    sleep(2)

# --- Existing code above remains unchanged ---

def init_kspeak():
    """Initializes the TTS system and starts background threads."""
    pygame.mixer.init()
    STOP_SPEECH_EVENT.clear()
    STOP_TEXT_PROCESSING_EVENT.clear()  # Clear the event at startup
    HOT_WORD_DECT_IS_ON_EVENT.set()
    # Start clap detection in the background.
    threading.Thread(target=clap_detection, daemon=True).start()
    # Start the TTS worker thread.
    threading.Thread(target=tts_worker, daemon=True).start()

def speak(text: str):
    """Wrapper that queues text for asynchronous TTS processing."""
    # You can add additional processing here if needed.
    if not STOP_TEXT_PROCESSING_EVENT.is_set():
        text_queue.put(text)

if __name__ == "__main__":
    # Initialize all the systems.
    init_kspeak()
    L = t()
    print(f"==> {AI_Name} AI: ", end="")

    # A simple main loop that calls speak() on each text chunk.
    for chunk in text_stream():
        print(chunk, flush=True, end='')
        speak(chunk)

    # Signal the worker to finish processing.
    text_queue.put(None)
    text_queue.join()  # Wait until all text has been processed.
    
    # Ensure any remaining audio is played.
    while not global_buffer.empty():
        sleep(0.1)
    time_taken = str(t()-L)[:4]    
    print(f"\nTime Taken: {time_taken}s")


# old usage
# if __name__ == "__main__":
#     pygame.mixer.init()
#     L = t()
#     STOP_SPEECH_EVENT.clear()
#     STOP_TEXT_PROCESSING_EVENT.clear()  # Clear the new event at startup
#     HOT_WORD_DECT_IS_ON_EVENT.set()
#     threading.Thread(target=clap_detection, daemon=True).start()
#     worker = threading.Thread(target=tts_worker, daemon=False)
#     worker.start()
#     print(f"==> {AI_Name} AI: ", end="")
#     for chunk in text_stream():
#         if STOP_TEXT_PROCESSING_EVENT.is_set():
#             break  # Stop yielding new chunks if processing was stopped
#         text_queue.put(chunk)
#         print(chunk, flush=True, end='')
#     text_queue.put(None)
#     text_queue.join()  # Wait until the TTS worker has processed all chunks.
#     worker.join()
#     while not global_buffer.empty():
#         sleep(0.1)
#     time_taken = str(t()-L)[:4]    
#     print(f"\nTime Taken: {time_taken}s")