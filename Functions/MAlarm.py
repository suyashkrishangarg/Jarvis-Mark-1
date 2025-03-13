import time
import datetime
import simpleaudio as sa
import threading
import os
if os.name == "nt":
    import msvcrt
event = threading.Event()
# Load the audio file using SimpleAudio
wave_obj = sa.WaveObject.from_wave_file(r"Resources\The Box.wav")

def play_alarm(wave_obj):
    """Plays the specified audio object."""
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait for the audio to finish playing

def set_alarm(alarm_time, music_path=r"Resources\The Box.wav",k=False):
    """Sets the alarm to play the chosen music at the specified time."""
    alarm_time = alarm_time.lower()  # Convert user input to lowercase

    try:
        if "am" in alarm_time or "pm" in alarm_time:
            # 12-hour clock format
            hour, minute = map(int, alarm_time.split(":")[:2])
            if "pm" in alarm_time and hour < 12:
                hour += 12
            alarm_time = datetime.time(hour, minute)
        else:
            # 24-hour clock format
            hour, minute = map(int, alarm_time.split(":"))
            alarm_time = datetime.time(hour, minute)

        now = datetime.datetime.now().time()
        if alarm_time <= now:
            raise ValueError("Alarm time must be in the future.")

        # Calculate the time difference in seconds until the alarm should play
        time_diff = (datetime.datetime.combine(datetime.date.today(), alarm_time) - datetime.datetime.now()).seconds
        print("Alarm Set!")

        # Sleep for the calculated time difference before playing the music
        time.sleep(time_diff)
        print("Hey, Alarm is ringing!")
        print("Press any key to stop Alarm")
        play_obj = wave_obj.play()
        while play_obj.is_playing():
        # Use get_char or getch depending on platform
            if os.name == "nt":
                key = msvcrt.getch()
            else:
                key = k
        # Stop playback if any key is pressed
            if key:
                play_obj.stop()
                break
        print(f"Alarm played \"{music_path.split('/')[-1]}\" at", alarm_time.strftime("%I:%M %p"))

    except ValueError as e:
        print(f"Invalid alarm time: {e}")

def Set_Alarm(Query):
    # Query = Query.replace(',',':') 
    alarm_process = threading.Thread(target=set_alarm, args=(Query,))
    alarm_process.start()
    return "Done"

def stop_Alarm():
    print("Alarm Stopped!")
    event.set()
    
print("==> Alarm Loaded!")

if __name__ == "__main__":
    Set_Alarm("20:10")
    input()
    stop_Alarm()