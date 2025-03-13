import os
import sys
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)
import io
import contextlib
import datetime
import webbrowser
import pywhatkit
import pyautogui
import requests as rq
import AppOpener
from CommonFunctions.Player import video_downloader
from CommonFunctions.Player import song_downloader
from Functions.MAlarm import Set_Alarm
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from API_keys import Gemini_api_key

# Additional libraries for new tools
import qrcode
import secrets
import string
import platform
import glob
import time
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None
from bs4 import BeautifulSoup

# Ensure current directory is in sys.path
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Initialize requests session
requests = rq.Session()

# Set up current time
current_time = datetime.datetime.now()
date_formatted = current_time.strftime("%Y")

# Initialize genai client
client = genai.Client(api_key=Gemini_api_key)
model_id = "gemini-2.0-flash"

# Define google search tool for genai
google_search_tool = Tool(google_search=GoogleSearch())

# Initialize the tools list with existing tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "searches the web to get realtime information.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "query for search",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Website_to_open",
            "description": "opens the specific website on a given url",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "url to open",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_video_or_song",
            "description": "plays a video or song by its description provided",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "description of the song or video to play",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_or_close_tab",
            "description": "uses pyautogui to open or close tabs",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "key stroke, can be 'w' or 't'",
                    },
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "video_downloader",
            "description": "downloads the video user currently on",
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "song_downloader",
            "description": "downloads the song user currently on",
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Set_Alarm",
            "description": "sets the alarm on the given time, takes the time only in 24 hour format, e.g., '18:00'",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "Query": {
                        "type": "string",
                        "description": "alarm time to be set",
                    },
                },
                "required": ["Query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Returns the weather in the given city in degrees Celsius",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "code_executer",
            "description": "Executes and returns the output of the given python code. Returns any errors if they occur.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to execute",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Translates given text to a specified language.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate",
                    },
                    "dest_language": {
                        "type": "string",
                        "description": "Destination language code (e.g., 'en', 'fr')",
                    },
                },
                "required": ["text", "dest_language"],
            },
        },
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "convert_currency",
    #         "description": "Converts an amount from one currency to another using current exchange rates.",
    #         "strict": True,
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "amount": {
    #                     "type": "number",
    #                     "description": "Amount to convert",
    #                 },
    #                 "from_currency": {
    #                     "type": "string",
    #                     "description": "Source currency code (e.g., 'USD')",
    #                 },
    #                 "to_currency": {
    #                     "type": "string",
    #                     "description": "Target currency code (e.g., 'EUR')",
    #                 },
    #             },
    #             "required": ["amount", "from_currency", "to_currency"],
    #         },
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "random_joke",
    #         "description": "Fetches a random joke from an online API.",
    #         "strict": True,
    #         "parameters": {"type": "object", "properties": {}},
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "random_quote",
    #         "description": "Fetches a random inspirational quote.",
    #         "strict": True,
    #         "parameters": {"type": "object", "properties": {}},
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_definition",
    #         "description": "Returns the definition of a given word.",
    #         "strict": True,
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "word": {
    #                     "type": "string",
    #                     "description": "Word to define",
    #                 },
    #             },
    #             "required": ["word"],
    #         },
    #     },
    # },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot and saves it to the specified filename.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename (with extension) to save the screenshot",
                    },
                },
                "required": ["filename"],
            },
        },
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "convert_temperature",
    #         "description": "Converts temperature between Celsius and Fahrenheit.",
    #         "strict": True,
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "value": {
    #                     "type": "number",
    #                     "description": "Temperature value to convert",
    #                 },
    #                 "from_unit": {
    #                     "type": "string",
    #                     "description": "Current unit ('C' or 'F')",
    #                 },
    #                 "to_unit": {
    #                     "type": "string",
    #                     "description": "Target unit ('C' or 'F')",
    #                 },
    #             },
    #             "required": ["value", "from_unit", "to_unit"],
    #         },
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "generate_qr",
    #         "description": "Generates a QR code for the given text and saves it to a file.",
    #         "strict": True,
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "text": {
    #                     "type": "string",
    #                     "description": "Text/data to encode in the QR code",
    #                 },
    #                 "filename": {
    #                     "type": "string",
    #                     "description": "Filename to save the QR code image",
    #                 },
    #             },
    #             "required": ["text", "filename"],
    #         },
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "generate_password",
    #         "description": "Generates a secure random password of a specified length.",
    #         "strict": True,
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "length": {
    #                     "type": "integer",
    #                     "description": "Length of the password",
    #                 },
    #             },
    #             "required": ["length"],
    #         },
    #     },
    # },
    {
        "type": "function",
        "function": {
            "name": "ip_lookup",
            "description": "Looks up geographical and network details for a given IP address.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "ip_address": {
                        "type": "string",
                        "description": "IP address to lookup",
                    },
                },
                "required": ["ip_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Returns information about the system's OS, hardware, and processor.",
            "strict": True,
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_search",
            "description": "Searches for files in a directory matching a given pattern.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (e.g., '*.txt')",
                    },
                },
                "required": ["directory", "pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ocr_image",
            "description": "Performs Optical Character Recognition (OCR) on an image to extract text.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file",
                    },
                },
                "required": ["image_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_scraper",
            "description": "Scrapes and returns all text content from the given URL.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Sets a timer for a specified number of seconds. (Note: This function will block execution.)",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "integer",
                        "description": "Number of seconds for the timer",
                    },
                },
                "required": ["seconds"],
            },
        },
    },
    # --- NEW: open_or_close_app tool definition using app opener library ---
    {
        "type": "function",
        "function": {
            "name": "open_or_close_software",
            "description": "Opens or closes a windows application using the app opener library.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform: 'open' or 'close'",
                    },
                    "website": {
                        "type": "string",
                        "description": "Website URL to open if the application is not installed",
                    },
                },
                "required": ["app_name", "action"],
            },
        },
    },
    # --- NEW: delete_tool tool definition ---
    {
        "type": "function",
        "function": {
            "name": "delete_tool",
            "description": "Deletes an existing tool from the system by name.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to delete",
                    },
                },
                "required": ["tool_name"],
            },
        },
    },
]

# Mapping of function names to their implementations
available_tools = {
    "web_search": None,
    "Website_to_open": None,
    "play_video_or_song": None,
    "open_or_close_tab": None,
    "video_downloader": None,
    "song_downloader": None,
    "Set_Alarm": None,
    "get_weather": None,
    "code_executer": None,
    "translate_text": None,
    "convert_currency": None,
    "random_joke": None,
    "random_quote": None,
    "get_definition": None,
    "take_screenshot": None,
    "convert_temperature": None,
    "generate_qr": None,
    "generate_password": None,
    "ip_lookup": None,
    "get_system_info": None,
    "file_search": None,
    "ocr_image": None,
    "web_scraper": None,
    "set_timer": None,
    "open_or_close_software": None,  # NEW: To be registered below
    "delete_tool": None,        # NEW: To be registered below
}


# Function Implementations

def web_search(query: str):
    response = client.models.generate_content(
        model=model_id,
        contents=query + " Give full information in detail and also give all the sourcees and links at the end.",
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    return response.text

def Website_to_open(url):
    webbrowser.open(url)
    return "Done"

def play_video_or_song(name):
    pywhatkit.playonyt(name)
    return "Done"

def open_or_close_tab(key):
    pyautogui.hotkey('ctrl', key)
    return "Done"

def get_weather(city):
    api_key = "a03117d3233b4f4c9c3175538241906"
    c_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=yes"
    coordinates = requests.get(c_url, timeout=10)
    return coordinates.json()

def code_executer(code: str):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code)
    except Exception as e:
        return f"Error: {e}"
    result = output.getvalue()
    return result if result else "Code executed successfully."

def translate_text(text: str, dest_language: str):
    from googletrans import Translator
    global_translator = Translator()
    translation = global_translator.translate(text, dest=dest_language)
    return translation.text

def convert_currency(amount: float, from_currency: str, to_currency: str):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
    response = requests.get(url, timeout=10)
    data = response.json()
    rate = data['rates'].get(to_currency.upper())
    if rate:
        return amount * rate
    else:
        return f"Conversion rate from {from_currency} to {to_currency} not found."

def random_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url, timeout=10)
    joke_data = response.json()
    return f"{joke_data['setup']} {joke_data['punchline']}"

def random_quote():
    url = "https://api.quotable.io/random"
    response = requests.get(url, timeout=10)
    quote_data = response.json()
    return f"{quote_data['content']} — {quote_data['author']}"

def get_definition(word: str):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url, timeout=10)
    data = response.json()
    if isinstance(data, list) and data:
        meanings = data[0].get("meanings", [])
        if meanings:
            definitions = meanings[0].get("definitions", [])
            if definitions:
                return definitions[0].get("definition", "No definition found.")
    return "No definition found."

def take_screenshot(filename: str):
    screenshot = pyautogui.screenshot()
    screenshot.save
    return f"Screenshot saved as {filename}"

def convert_temperature(value: float, from_unit: str, to_unit: str):
    if from_unit.lower() == "c" and to_unit.lower() == "f":
        return (value * 9/5) + 32
    elif from_unit.lower() == "f" and to_unit.lower() == "c":
        return (value - 32) * 5/9
    else:
        return "Conversion not supported."

def generate_qr(text: str, filename: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)
    return f"QR Code saved as {filename}"

def generate_password(length: int):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def ip_lookup(ip_address: str):
    url = f"http://ip-api.com/json/{ip_address}"
    response = requests.get(url, timeout=10)
    return response.json()

def get_system_info():
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }

def file_search(directory: str, pattern: str):
    search_path = os.path.join(directory, pattern)
    return glob.glob(search_path)

def ocr_image(image_path: str):
    if pytesseract and Image:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
    else:
        return "pytesseract or PIL not installed."

def web_scraper(url: str):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def set_timer(seconds: int):
    time.sleep(seconds)
    return f"Timer for {seconds} seconds finished."

# --- NEW TOOL: open_or_close_app using AppOpener library ---
def open_or_close_software(app_name: str, action: str, website: str = None):
    """
    Uses the AppOpener library to open or close an application.
    If the application is not installed and a website is provided, opens the website.
    """
    try:
        if action.lower() == 'open':
            result = AppOpener.open(app_name, match_closest=True, throw_error=True)
            if not result and website:
                webbrowser.open(website)
                return f"{app_name} is not installed. Opened its website."
            return f"{app_name} opened successfully."
        elif action.lower() == 'close':
            result = AppOpener.close(app_name, match_closest=True, throw_error=True)
            if result:
                return f"{app_name} closed successfully."
            else:
                return f"Failed to close {app_name}."
        else:
            return "Invalid action specified. Use 'open' or 'close'."
    except Exception as e:
        return f"Error using AppOpener: {e}"

# --- NEW TOOL: delete_tool ---
def delete_tool(tool_name: str):
    """
    Deletes an existing tool from the system by name.
    Removes the tool from both the tools list and the available_tools dictionary.
    """
    global tools, available_tools
    if tool_name in available_tools:
        del available_tools[tool_name]
    else:
        return f"Tool '{tool_name}' does not exist in available_tools."
    removed = False
    for entry in tools[:]:
        if entry.get("function", {}).get("name") == tool_name:
            tools.remove(entry)
            removed = True
    if removed:
        return f"Tool '{tool_name}' successfully deleted."
    else:
        return f"Tool '{tool_name}' not found in tools list."

# --- New Tool Maker Tool: create_new_tool ---
def create_new_tool(tool_definition: dict):
    """
    Creates and registers a new tool from a JSON definition.
    The tool_definition must include keys: 'name', 'description', 'parameters', and 'code'.
    """
    global tools, available_tools
    required_keys = ['name', 'description', 'parameters', 'code']
    for key in required_keys:
        if key not in tool_definition:
            return f"Error: Missing key '{key}' in tool definition."

    tool_name = tool_definition['name']
    code_str = tool_definition['code']
    try:
        exec(code_str, globals())
    except Exception as e:
        return f"Error executing code: {e}"

    if tool_name not in globals():
        return f"Error: Function '{tool_name}' not defined in the provided code."

    available_tools[tool_name] = globals()[tool_name]

    new_tool_entry = {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_definition['description'],
            "parameters": tool_definition['parameters'],
        }
    }
    tools.append(new_tool_entry)
    
    try:
        with open(__file__, "a") as f:
            f.write("\n\n# --- Dynamically Added Tool ---\n")
            f.write(code_str)
            f.write("\n")
            f.write(f"# Tool entry for {tool_name} added to tools list.\n")
    except Exception as e:
        print(f"Warning: Tool '{tool_name}' added in session but file update failed: {e}")
    
    return f"Tool '{tool_name}' successfully added."

# Register the dynamic tool maker
tools.append({
    "type": "function",
    "function": {
        "name": "create_new_tool",
        "description": "Creates and registers a new tool from a JSON definition. Requires keys: 'name', 'description', 'parameters', and 'code'.",
        "parameters": {
            "type": "object",
            "properties": {
                "tool_definition": {
                    "type": "object",
                    "description": "New tool definition as JSON."
                }
            },
            "required": ["tool_definition"]
        },
    },
})
available_tools["create_new_tool"] = create_new_tool

# Register remaining implementations in available_tools
available_tools["web_search"] = web_search
available_tools["Website_to_open"] = Website_to_open
available_tools["play_video_or_song"] = play_video_or_song
available_tools["open_or_close_tab"] = open_or_close_tab
available_tools["get_weather"] = get_weather
available_tools["code_executer"] = code_executer
available_tools["translate_text"] = translate_text
# available_tools["convert_currency"] = convert_currency
# available_tools["random_joke"] = random_joke
# available_tools["random_quote"] = random_quote
# available_tools["get_definition"] = get_definition
available_tools["take_screenshot"] = take_screenshot
# available_tools["convert_temperature"] = convert_temperature
# available_tools["generate_qr"] = generate_qr
# available_tools["generate_password"] = generate_password
available_tools["ip_lookup"] = ip_lookup
available_tools["get_system_info"] = get_system_info
available_tools["file_search"] = file_search
available_tools["ocr_image"] = ocr_image
available_tools["web_scraper"] = web_scraper
available_tools["set_timer"] = set_timer
available_tools["open_or_close_software"] = open_or_close_software
available_tools["delete_tool"] = delete_tool
available_tools["Set_Alarm"] = Set_Alarm
available_tools["video_downloader"] = video_downloader
available_tools["song_downloader"] = song_downloader

if __name__=="__main__":
    take_screenshot(r"C:\Users\suyas\OneDrive\Pictures\Screenshots")