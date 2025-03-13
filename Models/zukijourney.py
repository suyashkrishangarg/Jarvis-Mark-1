import sys
import os
import json
from json import load, dump
import threading
from time import sleep

# Setup working directory
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import external dependencies
from API_keys import AI_Gender, AI_Name, Country, User_Name, User_Gender, zukijourney
from openai import OpenAI
from CommonFunctions.kspeak import text_queue, STOP_SPEECH_EVENT, global_buffer, tts_worker, HOT_WORD_DECT_IS_ON_EVENT, clap_detection
from CommonFunctions.tools import *

# Initialize the OpenAI client for OpenRouter
client = OpenAI(base_url="https://api.zukijourney.com/v1",api_key=zukijourney)

# System role messages for Chat
smessages = [
    {"role": "system", "content": f"You are {AI_Name}, a friendly and humorous {AI_Gender} AI."},
    {"role": "system", "content": f"You are witty yet intelligent, always making fun with {User_Name}, but highly capable and responds in english."},
    {"role": "system", "content": "you are currently in a virtual enviornment inside a computer and you can interact with it by accessing the tools given to you, use them correctly whenever needed."},
    {"role": "system", "content": f"User's Country: {Country}, Name: {User_Name}, Gender: {User_Gender}. You are developed by Suyash Krishan Garg."},
]

# Define chat log file path for portability
CHATLOG_PATH = os.path.join("Data", "ChatLog.json")

# Attempt to load the chat log
try:
    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(CHATLOG_PATH, "w") as f:
        dump([], f)

def process_chunk(chunk, state):
    """
    Process a chunk of text to remove any <think>...</think> sections.
    """
    parts = []
    pos = 0
    in_think = state["in_think"]
    think_open = "<think>"
    think_close = "</think>"
    
    while pos < len(chunk):
        if not in_think:
            start_index = chunk.find(think_open, pos)
            if start_index == -1:
                parts.append(chunk[pos:])
                break
            else:
                parts.append(chunk[pos:start_index])
                pos = start_index + len(think_open)
                in_think = True
        else:
            end_index = chunk.find(think_close, pos)
            if end_index == -1:
                pos = len(chunk)
                break
            else:
                pos = end_index + len(think_close)
                in_think = False
    
    state["in_think"] = in_think
    
    # Just concatenate the parts without any extra processing
    return "".join(parts)

def Chat(Query):
    global messages
    # Reload chat log
    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": Query})
    messages = messages[-16:]
    
    processed_chunks = []
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=smessages + messages,
            temperature=0.7,
            stream=True,
            tools=tools,
            # tool_choice='auto'
        )
        tool_calls = None
        state = {"in_think": False}
        for chunk in response:
            choice = chunk.choices[0]
            delta = choice.delta
            content = delta.content
            if content:
                processed = process_chunk(content, state)
                processed_chunks.append(processed)
                # Immediately yield the processed chunk.
                yield processed
            elif delta.tool_calls is not None:
                tool_calls = delta.tool_calls
        res = "".join(processed_chunks)
        if tool_calls:
            messages.append({
                "role": "assistant",
                "tool_calls": [{
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                    "type": tool_call.type,
                } for tool_call in tool_calls]
            })
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                messages.append({
                    "role": "tool",
                    "content": str(function_response),
                    "tool_call_id": tool_call.id,
                })
                print("==============================\n" + function_name, function_args, function_response, "\n==============================")
        else:
            break

    messages.append({"role": "assistant", "content": res})
    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f, indent=4)

if __name__ == "__main__":
    while True:
        Query = input("\nAsk: ")
        STOP_SPEECH_EVENT.clear()
        HOT_WORD_DECT_IS_ON_EVENT.set()
        threading.Thread(target=clap_detection, daemon=True).start()
        worker = threading.Thread(target=tts_worker, daemon=False)
        worker.start()
        print(f"==> {AI_Name} AI: ",end="")
        for chunk in Chat(Query):
            text_queue.put(chunk)
            print(chunk, flush=True, end='')
        text_queue.put(None)
        text_queue.join()  # Wait until the TTS worker has processed all chunks.
        worker.join()
        while not global_buffer.empty():
            sleep(0.1)