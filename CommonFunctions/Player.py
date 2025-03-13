import pywhatkit
import pytube
import keyboard
import pyperclip as pi
from time import sleep

def PlayOnYT(song_name):

    # Use pywhatkit to search and play the first video directly
    pywhatkit.playonyt(song_name)

    # Print a message for user confirmation
    res = (f"Playing '{song_name.upper()}' on YouTube...")
    return res

def download_video(url, output_path=r'Downloads\videos'):
    try:
        # Create a YouTube object
        yt = pytube.YouTube(url)

        # Get the video streams in descending order of quality
        video_streams = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()

        # Get the video title for naming the downloaded file
        video_title = yt.title

        # Specify the output path
        download_path = f"{output_path}\\{video_title}.mp4"

        # Download the video to the specified path
        print(f"Downloading video: {video_title}...")
        video_streams.download(output_path=output_path, filename=video_title+'.mp4')
        print(f"Download completed! Video saved at: {download_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def video_downloader():
    keyboard.press("f6")
    sleep(0.5)
    keyboard.press_and_release("ctrl + c")
    sleep(0.5)
    url = pi.paste()
    print(url)
    download_video(url)
    return "Done"
# video_downloader()

def clipboard_data():
    keyboard.press_and_release("ctrl + c")
    data = pi.paste()
    return data

def Search(Query):
    pywhatkit.search(Query)

    # Print a message for user confirmation
    res = (f"Here's What I Found For '{Query.upper()}' on Google...")
    return res

def download_audio(url, output_path=r'Downloads\songs'):
   try:
       # Create a YouTube object
       yt = pytube.YouTube(url)

       # Get the audio stream
       audio_stream = yt.streams.filter(only_audio=True).first()

       # Get the video title for naming the downloaded file
       audio_title = yt.title

       # Specify the output path and filename with .mp3 extension
       download_path = f"{output_path}\\{audio_title}.mp3"

       # Download the audio to the specified path
       print(f"Downloading audio: {audio_title}...")
       audio_stream.download(output_path=output_path, filename=audio_title + '.mp3')
       print(f"Download completed! Audio saved at: {download_path}")

   except Exception as e:
       print(f"An error occurred: {e}")

def song_downloader():
    keyboard.press("f6")
    sleep(0.5)
    keyboard.press_and_release("ctrl + c")
    sleep(0.5)
    url = pi.paste()
    print(url)
    download_audio(url)
    return "Done"

print("==> Player Loaded!")

# video_withsubtitles_downloader()
# song_downloader()
# Search("elon musk")