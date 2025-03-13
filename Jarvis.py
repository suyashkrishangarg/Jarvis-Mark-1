from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Models.groq import Chat
# from Backend.Automation import Automation
from CommonFunctions.SpeechRecoggui import speechrecognition
# from Backend.Chatbot import ChatBot
from CommonFunctions.kspeak import text_queue, STOP_SPEECH_EVENT, global_buffer, tts_worker, HOT_WORD_DECT_IS_ON_EVENT, clap_detection
from API_keys import AI_Name, User_Name
from time import sleep
import threading
import json

Username = User_Name
Assistantname = AI_Name
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
        content = file.read()
    if len(content) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        # Use get() to safely access 'content' with a default value if it's missing.
        content = entry.get("content", "[No Content]")
        if entry["role"] == "user":
            formatted_chatlog += f"User: {content}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {content}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        Data = file.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    # Clear GUI responses so old chat history is not visible.
    ShowTextToScreen("")
    # Optionally remove or comment out calls to load old history:
    # ShowDefaultChatIfNoChats()
    # ChatLogIntegration()
    # ShowChatsOnGUI()


InitialExecution()

def MainExecution():
    SetAssistantStatus("Listening ... ")
    before_q = f"You : "
    ShowTextToScreen(before_q)
    
    # Stream the query as it's recognized
    Query = speechrecognition()
    conversation_history = before_q + f"{Query}\n"
    ShowTextToScreen(conversation_history)
    
    SetAssistantStatus("Thinking ... ")

    # Ensure stop flag is cleared and enable clap detection.
    STOP_SPEECH_EVENT.clear()
    HOT_WORD_DECT_IS_ON_EVENT.set()
    threading.Thread(target=clap_detection, daemon=True).start()

    # Start the TTS worker as a non-daemon thread so you can wait for it to finish.
    worker = threading.Thread(target=tts_worker, daemon=False)
    worker.start()

    assistant_response = ""
    before_r = conversation_history + f"{Assistantname} : "
    ShowTextToScreen(before_r)
    
    # Stream Chat response and push each sentence to the TTS text queue.
    for sentence in Chat(Query):
         text_queue.put(sentence)
         assistant_response += sentence
         updated_history = before_r + f"{assistant_response}\n"
         ShowTextToScreen(updated_history)
    
    # Signal end of streaming:
    text_queue.put(None)
    text_queue.join()  # Wait until the TTS worker has processed all chunks.
    worker.join()  # Ensure the TTS thread has ended.
    
    # Wait until the audio buffer is fully drained.
    while not global_buffer.empty():
         sleep(0.1)
    
    # Finally, update status to show the prompt for next input.
    SetAssistantStatus("You : ")
    
    return True



def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ... " in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ... ")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
