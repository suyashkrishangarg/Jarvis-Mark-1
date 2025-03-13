import requests
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import time

# Configuration: using the voice "Brian" as an example.
VOICE_ID = "nPczCjzI2devNBz1zQrb"  # ID for the "Brian" voice.
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
HEADERS = {"User-Agent": "TTS-Streamer/1.0"}
PARAMS = {"allow_unauthenticated": "1"}

def tts_stream(text):
    """
    Splits the input text into sentences, generates TTS audio for each sentence
    using the ElevenLabs API, and plays the audio as soon as it's available.
    """
    # A simple split by period; for more robust splitting consider using nltk.sent_tokenize.
    sentences = text.split('. ')
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        # Ensure sentence ends with punctuation.
        if sentence[-1] not in ".!?":
            sentence += "."
        
        # Prepare the payload for the API call.
        json_data = {"text": sentence, "model_id": "eleven_flash_v2_5"}
        
        # Try until the API call succeeds.
        while True:
            try:
                response = requests.post(API_URL, params=PARAMS, headers=HEADERS, json=json_data, timeout=20)
                response.raise_for_status()
                audio_data = response.content
                break  # Exit retry loop on success.
            except requests.RequestException as e:
                print(f"Error generating audio for: '{sentence}'\nError: {e}\nRetrying in 1 second...")
                time.sleep(1)
        
        # Convert the MP3 bytes into an AudioSegment and play it immediately.
        try:
            audio_segment = AudioSegment.from_file(BytesIO(audio_data), format="mp3")
            play(audio_segment)
        except Exception as e:
            print(f"Error playing audio: {e}")

if __name__ == "__main__":
    text = input("Enter text to stream: ")
    tts_stream(text)
