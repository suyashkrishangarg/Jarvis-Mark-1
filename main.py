import os
import sys
import threading
from time import sleep
import re

# Ensure current directory is on the path
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Define threaded import functions
def load_kspeak():
    global text_queue, STOP_SPEECH_EVENT, global_buffer, tts_worker, HOT_WORD_DECT_IS_ON_EVENT, clap_detection
    from CommonFunctions.kspeak import text_queue, STOP_SPEECH_EVENT, global_buffer, tts_worker, HOT_WORD_DECT_IS_ON_EVENT, clap_detection

def load_speech_recognition():
    global speechrecognition
    from CommonFunctions.speechrecogwhisper import speechrecognition

def load_AI_Chat():
    global AI_Name, Chat 
    from API_keys import AI_Name
    from Models.groq import Chat

# Create threads for each import
threads = [
    threading.Thread(target=load_kspeak),
    threading.Thread(target=load_speech_recognition),
    threading.Thread(target=load_AI_Chat),
]

# Start all threads
for t in threads:
    t.start()
    
from CommonFunctions.tools import *

# Wait for all threads to finish
for t in threads:
    t.join()

# Now, all modules have been imported concurrently.

# Define a regex pattern for emojis
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251" 
                           "]+", flags=re.UNICODE)

def filter_queries(query):
    """
    Processes the incoming query by matching and executing multiple command patterns.
    It iteratively executes commands and removes them from the query until no commands remain.
    Returns False if at least one command was processed, True if no commands were processed.
    """
    global answer  # assume answer is a global variable
    original_query = query
    commands_processed = False
    all_responses = []
    
    # Keep processing until no more commands are found
    while query.strip():
        command_found = False
        lower_query = query.lower()
        
        # 1. Play a song or video
        if lower_query.startswith("play "):
            # Extract the song name - take everything until the next command keyword or the end
            remaining = query[5:].strip()
            end_pos = find_next_command_start(remaining)
            if end_pos > 0:
                song = remaining[:end_pos].strip()
                query = remaining[end_pos:].strip()
            else:
                song = remaining
                query = ""
                
            play_video_or_song(song)
            response = f"{song} is now playing."
            all_responses.append(response)
            command_found = True
        
        # 2. Download video
        elif lower_query.startswith("download this video"):
            video_downloader()
            response = "Video Downloaded Sir!"
            all_responses.append(response)
            query = query[len("download this video"):].strip()
            command_found = True
        
        # 3. Download song
        elif lower_query.startswith("download this song"):
            song_downloader()
            response = "Song Downloaded Sir!"
            all_responses.append(response)
            query = query[len("download this song"):].strip()
            command_found = True
        
        # 4. Open or close a tab
        elif (lower_query.startswith("open") or lower_query.startswith("close")) and "tab" in lower_query:
            action = "open" if lower_query.startswith("open") else "close"
            if action == "open":
                open_or_close_tab('t')
                response = "Tab opened."
            else:
                open_or_close_tab("w")
                response = "Tab closed. Done Sir!"
            
            all_responses.append(response)
            # Remove the command from the query
            query = remove_command(query, action, "tab")
            command_found = True
        
        # 5. Open popular websites
        elif lower_query.startswith("open") and any(site in lower_query for site in ["instagram", "amazon", "insta", "youtube", "whatsapp", "twitter", "brave", "browser", "collab", "facebook"]):
            sites_opened = []
            
            # Check for each website in the query
            remaining_query = query
            for site_keyword, site_url in [
                # ("insta", "https://www.instagram.com/"),
                ("instagram", "https://www.instagram.com/"),
                ("whatsapp", "https://web.whatsapp.com/"),
                ("twitter", "https://www.twitter.com/"),
                ("amazon", "https://www.amazon.in/"),
                ("youtube", "https://www.youtube.com/"),
                ("facebook", "https://www.facebook.com/"),
                ("colab", "https://www.colab.research.google.com/"),
                ("collab", "https://www.colab.research.google.com/")
            ]:
                if site_keyword in lower_query:
                    Website_to_open(site_url)
                    sites_opened.append(site_keyword)
                    # Remove this site from the query
                    remaining_query = remove_site_from_query(remaining_query, site_keyword)
            
            # Handle browser separately since it uses a different function
            if "browser" in lower_query or "brave" in lower_query:
                try:
                    os.startfile('brave.exe')
                except Exception:
                    os.startfile('chrome.exe')
                sites_opened.append("browser")
                remaining_query = remove_site_from_query(remaining_query, "browser")
                remaining_query = remove_site_from_query(remaining_query, "brave")
            
            if sites_opened:
                response = f"Opened: {', '.join(sites_opened)}. Done Sir!"
                all_responses.append(response)
                query = remaining_query.strip()
                if query.lower().startswith("open "):
                    query = query[5:].strip()
                command_found = True
        
        # 6. Close browser (Brave/Chrome)
        elif lower_query.startswith("close") and ("brave" in lower_query or "browser" in lower_query):
            try:
                os.system('taskkill /IM brave.exe /F')
            except Exception:
                os.system('taskkill /IM chrome.exe /F')
            response = "Browser closed. Done Sir!"
            all_responses.append(response)
            query = remove_command(query, "close", "brave" if "brave" in lower_query else "browser")
            command_found = True
        
        # 7. Mouse click command
        elif lower_query.startswith("click here") or lower_query == "click":
            pyautogui.click(button='left')
            response = "Click performed. Done Sir!"
            all_responses.append(response)
            query = query[len("click here" if lower_query.startswith("click here") else "click"):].strip()
            command_found = True
        
        # 8. Type command with "enter"
        elif ((lower_query.startswith("type here") and "enter" in lower_query) or 
              (lower_query.startswith("type") and "enter" in lower_query) or 
              (lower_query.startswith("write") and "enter" in lower_query)):
            if lower_query.startswith("type here"):
                content_start = len("type here ")
            elif lower_query.startswith("type"):
                content_start = len("type ")
            elif lower_query.startswith("write"):
                content_start = len("write ")
                
            # Find where the content ends (at the next command or end of string)
            content_end = find_next_command_start(query[content_start:])
            if content_end > 0:
                content = query[content_start:content_start + content_end].strip()
                query = query[content_start + content_end:].strip()
            else:
                content = query[content_start:].strip()
                query = ""
                
            if content.endswith("and press enter"):
                content = content[:-len("and press enter")].strip()
            elif content.endswith("enter"):
                content = content[:-len("enter")].strip()
                
            pyautogui.typewrite(content)
            pyautogui.hotkey('enter')
            response = f"Typed '{content}' and pressed Enter. Done Sir!"
            all_responses.append(response)
            command_found = True
        
        # 9. Type command without "enter"
        elif lower_query.startswith("type here") or lower_query.startswith("type") or lower_query.startswith("write"):
            if lower_query.startswith("type here"):
                content_start = len("type here ")
            elif lower_query.startswith("type"):
                content_start = len("type ")
            elif lower_query.startswith("write"):
                content_start = len("write ")
                
            # Find where the content ends (at the next command or end of string)
            content_end = find_next_command_start(query[content_start:])
            if content_end > 0:
                content = query[content_start:content_start + content_end].strip()
                query = query[content_start + content_end:].strip()
            else:
                content = query[content_start:].strip()
                query = ""
                
            pyautogui.typewrite(content)
            response = f"Typed '{content}'. Done Sir!"
            all_responses.append(response)
            command_found = True
        
        # 10. "enter" key command
        elif lower_query == "enter" or lower_query.startswith("press enter") or lower_query.startswith("hit enter"):
            pyautogui.hotkey('enter')
            response = "Pressed Enter. Done Sir!"
            all_responses.append(response)
            
            if lower_query.startswith("press enter"):
                query = query[len("press enter"):].strip()
            elif lower_query.startswith("hit enter"):
                query = query[len("hit enter"):].strip()
            else:
                query = query[len("enter"):].strip()
                
            command_found = True
        
        # 11. Weather information: "weather in <city>"
        elif lower_query.startswith("weather in "):
            # Find the city name by taking everything until the next command or end
            city_start = len("weather in ")
            city_end = find_next_command_start(query[city_start:])
            
            if city_end > 0:
                city = query[city_start:city_start + city_end].strip()
                query = query[city_start + city_end:].strip()
            else:
                city = query[city_start:].strip()
                query = ""
                
            weather = get_weather(city)
            response = f"Weather in {city}: {weather}"
            all_responses.append(response)
            command_found = True
        
        # 12. Execute Python code: "run code: <code>"
        elif lower_query.startswith("run code:"):
            code_start = len("run code:")
            code_end = find_next_command_start(query[code_start:])
            
            if code_end > 0:
                code = query[code_start:code_start + code_end].strip()
                query = query[code_start + code_end:].strip()
            else:
                code = query[code_start:].strip()
                query = ""
                
            output = code_executer(code)
            response = f"Code execution result:\n{output}"
            all_responses.append(response)
            command_found = True
        
        # 13. Translate text: "translate <text> to <language>"
        elif lower_query.startswith("translate "):
            try:
                # Expecting format: "translate <text> to <language>"
                remaining = query[len("translate "):].strip()
                
                if " to " in remaining:
                    text_end = remaining.find(" to ")
                    text_to_translate = remaining[:text_end].strip()
                    
                    # Extract language and find where the command ends
                    lang_start = text_end + len(" to ")
                    lang_end = find_next_command_start(remaining[lang_start:])
                    
                    if lang_end > 0:
                        dest_language = remaining[lang_start:lang_start + lang_end].strip()
                        query = remaining[lang_start + lang_end:].strip()
                    else:
                        dest_language = remaining[lang_start:].strip()
                        query = ""
                    
                    translation = translate_text(text_to_translate, dest_language)
                    response = f"Translation: {translation}"
                else:
                    response = "Invalid translation command format."
                    query = query[len("translate "):].strip()
            except Exception as e:
                response = f"Error in translation command: {e}"
                query = query[len("translate "):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 14. Currency conversion: "convert <amount> <from_currency> to <to_currency>"
        elif lower_query.startswith("convert ") and " to " in lower_query and not lower_query.startswith("convert temperature"):
            try:
                # Example: "convert 100 usd to eur"
                parts = query.split()
                amount = float(parts[1])
                from_currency = parts[2]
                
                # Find the "to" keyword
                to_index = -1
                for i, word in enumerate(parts):
                    if word.lower() == "to" and i > 2:
                        to_index = i
                        break
                
                if to_index > 0 and to_index < len(parts) - 1:
                    to_currency = parts[to_index + 1]
                    conversion = convert_currency(amount, from_currency, to_currency)
                    response = f"{amount} {from_currency.upper()} = {conversion} {to_currency.upper()}"
                    
                    # Remove this command from query
                    command_end = query.find(to_currency) + len(to_currency)
                    if command_end < len(query):
                        query = query[command_end:].strip()
                    else:
                        query = ""
                else:
                    response = "Invalid currency conversion format."
                    query = query[len("convert "):].strip()
            except Exception as e:
                response = f"Error in currency conversion: {e}"
                # Skip to the next command if possible
                next_cmd = find_next_command_start(query[len("convert "):])
                if next_cmd > 0:
                    query = query[len("convert ") + next_cmd:].strip()
                else:
                    query = ""
                
            all_responses.append(response)
            command_found = True
        
        # 15. Tell a random joke
        elif "joke" in lower_query:
            joke = random_joke()
            response = joke
            all_responses.append(response)
            
            # Remove the joke command from the query
            joke_pos = lower_query.find("joke")
            before = query[:joke_pos].strip()
            after = query[joke_pos + 4:].strip()
            
            # Only keep text that might contain other commands
            if before.strip() and any(cmd in before.lower() for cmd in ["play", "open", "close", "type", "weather"]):
                query = before
            elif after.strip() and any(cmd in after.lower() for cmd in ["play", "open", "close", "type", "weather"]):
                query = after
            else:
                query = ""
                
            command_found = True
        
        # 16. Provide a random inspirational quote
        elif "quote" in lower_query:
            quote = random_quote()
            response = quote
            all_responses.append(response)
            
            # Remove the quote command from the query
            quote_pos = lower_query.find("quote")
            before = query[:quote_pos].strip()
            after = query[quote_pos + 5:].strip()
            
            # Only keep text that might contain other commands
            if before.strip() and any(cmd in before.lower() for cmd in ["play", "open", "close", "type", "weather"]):
                query = before
            elif after.strip() and any(cmd in after.lower() for cmd in ["play", "open", "close", "type", "weather"]):
                query = after
            else:
                query = ""
                
            command_found = True
        
        # 17. Define a word: "define <word>"
        elif lower_query.startswith("define "):
            word_start = len("define ")
            word_end = find_next_command_start(query[word_start:])
            
            if word_end > 0:
                word = query[word_start:word_start + word_end].strip()
                query = query[word_start + word_end:].strip()
            else:
                word = query[word_start:].strip()
                query = ""
                
            definition = get_definition(word)
            response = f"Definition of {word}: {definition}"
            all_responses.append(response)
            command_found = True
        
        # 18. Take a screenshot: "screenshot <filename>"
        elif lower_query.startswith("screenshot"):
            parts = lower_query.split()
            
            if len(parts) > 1:
                filename_start = len("screenshot ") 
                filename_end = find_next_command_start(query[filename_start:])
                
                if filename_end > 0:
                    filename = query[filename_start:filename_start + filename_end].strip()
                    query = query[filename_start + filename_end:].strip()
                else:
                    filename = query[filename_start:].strip()
                    query = ""
            else:
                filename = "screenshot.png"
                query = query[len("screenshot"):].strip()
                
            take_screenshot(filename)
            response = f"Screenshot taken and saved as {filename}"
            all_responses.append(response)
            command_found = True
        
        # 19. Convert temperature: "convert temperature <value> from <unit> to <unit>"
        elif lower_query.startswith("convert temperature"):
            try:
                # Example: "convert temperature 100 from c to f"
                parts = query.lower().split()
                
                # Find the value, from_unit, and to_unit
                value_index = -1
                from_index = -1
                to_index = -1
                
                for i, part in enumerate(parts):
                    if i > 1 and part.replace('.', '', 1).isdigit():
                        value_index = i
                    if part == "from" and value_index != -1 and i > value_index:
                        from_index = i
                    if part == "to" and from_index != -1 and i > from_index:
                        to_index = i
                
                if value_index != -1 and from_index != -1 and to_index != -1 and to_index < len(parts) - 1:
                    value = float(parts[value_index])
                    from_unit = parts[from_index + 1]
                    to_unit = parts[to_index + 1]
                    
                    converted = convert_temperature(value, from_unit, to_unit)
                    response = f"Converted temperature: {converted}"
                    
                    # Remove this command
                    command_end = query.lower().find(to_unit) + len(to_unit)
                    if command_end < len(query):
                        query = query[command_end:].strip()
                    else:
                        query = ""
                else:
                    response = "Invalid temperature conversion format."
                    query = query[len("convert temperature"):].strip()
            except Exception as e:
                response = f"Error in temperature conversion: {e}"
                query = query[len("convert temperature"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 20. Generate a QR code: "generate qr for <text> [save as <filename>]"
        elif lower_query.startswith("generate qr"):
            try:
                if " for " in lower_query:
                    text_start = lower_query.find(" for ") + len(" for ")
                    
                    # Check if "save as" is specified
                    if " save as " in lower_query[text_start:]:
                        save_as_pos = lower_query[text_start:].find(" save as ") + text_start
                        text_part = query[text_start:save_as_pos].strip()
                        
                        filename_start = save_as_pos + len(" save as ")
                        filename_end = find_next_command_start(query[filename_start:])
                        
                        if filename_end > 0:
                            filename = query[filename_start:filename_start + filename_end].strip()
                            query = query[filename_start + filename_end:].strip()
                        else:
                            filename = query[filename_start:].strip()
                            query = ""
                    else:
                        # No "save as" specified
                        text_end = find_next_command_start(query[text_start:])
                        if text_end > 0:
                            text_part = query[text_start:text_start + text_end].strip()
                            query = query[text_start + text_end:].strip()
                        else:
                            text_part = query[text_start:].strip()
                            query = ""
                        filename = "qr.png"
                    
                    generate_qr(text_part, filename)
                    response = f"QR Code generated for '{text_part}' and saved as {filename}"
                else:
                    response = "Invalid QR command format."
                    query = query[len("generate qr"):].strip()
            except Exception as e:
                response = f"Error generating QR code: {e}"
                query = query[len("generate qr"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 21. Generate a secure password: "generate password <length>"
        elif lower_query.startswith("generate password"):
            try:
                parts = query.split()
                if len(parts) > 2 and parts[2].isdigit():
                    length = int(parts[2])
                    password = generate_password(length)
                    response = f"Generated password: {password}"
                else:
                    # Default length if not specified
                    password = generate_password(12)
                    response = f"Generated password: {password}"
                
                query = query[len("generate password"):].strip()
                if len(parts) > 2 and parts[2].isdigit():
                    query = query[len(parts[2]):].strip()
            except Exception as e:
                response = f"Error generating password: {e}"
                query = query[len("generate password"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 22. IP lookup: "lookup ip <ip_address>"
        elif lower_query.startswith("lookup ip"):
            ip_start = len("lookup ip ")
            ip_end = find_next_command_start(query[ip_start:])
            
            if ip_end > 0:
                ip_address = query[ip_start:ip_start + ip_end].strip()
                query = query[ip_start + ip_end:].strip()
            else:
                ip_address = query[ip_start:].strip()
                query = ""
                
            info = ip_lookup(ip_address)
            response = f"IP Lookup result: {info}"
            all_responses.append(response)
            command_found = True
        
        # 23. System information: "system info"
        elif lower_query.startswith("system info"):
            info = get_system_info()
            response = f"System Info: {info}"
            all_responses.append(response)
            query = query[len("system info"):].strip()
            command_found = True
        
        # 24. File search: "search file in <directory> for <pattern>"
        elif lower_query.startswith("search file"):
            try:
                if " in " in lower_query and " for " in lower_query:
                    in_pos = lower_query.find(" in ") + len(" in ")
                    for_pos = lower_query.find(" for ", in_pos)
                    
                    directory = query[in_pos:for_pos].strip()
                    pattern_start = for_pos + len(" for ")
                    
                    pattern_end = find_next_command_start(query[pattern_start:])
                    if pattern_end > 0:
                        pattern = query[pattern_start:pattern_start + pattern_end].strip()
                        query = query[pattern_start + pattern_end:].strip()
                    else:
                        pattern = query[pattern_start:].strip()
                        query = ""
                    
                    files = file_search(directory, pattern)
                    response = f"Files found: {files}"
                else:
                    response = "Invalid file search command format."
                    query = query[len("search file"):].strip()
            except Exception as e:
                response = f"Error in file search: {e}"
                query = query[len("search file"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 25. OCR on image: "ocr image <image_path>"
        elif lower_query.startswith("ocr image"):
            image_start = len("ocr image ")
            image_end = find_next_command_start(query[image_start:])
            
            if image_end > 0:
                image_path = query[image_start:image_start + image_end].strip()
                query = query[image_start + image_end:].strip()
            else:
                image_path = query[image_start:].strip()
                query = ""
                
            result = ocr_image(image_path)
            response = f"OCR Result: {result}"
            all_responses.append(response)
            command_found = True
        
        # 26. Web scraper: "scrape website <url>"
        elif lower_query.startswith("scrape website"):
            url_start = len("scrape website ")
            url_end = find_next_command_start(query[url_start:])
            
            if url_end > 0:
                url = query[url_start:url_start + url_end].strip()
                query = query[url_start + url_end:].strip()
            else:
                url = query[url_start:].strip()
                query = ""
                
            result = web_scraper(url)
            # Limit output length for safety
            response = f"Scraped content (first 200 chars): {result[:200]}..."
            all_responses.append(response)
            command_found = True
        
        # 27. Set a timer: "set timer for <seconds> seconds"
        elif lower_query.startswith("set timer"):
            try:
                parts = query.lower().split()
                for_index = -1
                seconds_index = -1
                
                for i, part in enumerate(parts):
                    if part == "for" and i < len(parts) - 2:
                        for_index = i
                    if part == "seconds" and i > 0 and i < len(parts) - 1 and parts[i-1].isdigit():
                        seconds_index = i
                
                if for_index != -1 and seconds_index != -1:
                    seconds = int(parts[for_index + 1])
                    result = set_timer(seconds)
                    response = result
                    
                    # Remove this command
                    timer_end = query.lower().find("seconds") + len("seconds")
                    if timer_end < len(query):
                        query = query[timer_end:].strip()
                    else:
                        query = ""
                else:
                    response = "Invalid timer format."
                    query = query[len("set timer"):].strip()
            except Exception as e:
                response = f"Error setting timer: {e}"
                query = query[len("set timer"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 28. Open or close an application: "open app <app_name>" or "close app <app_name>"
        elif lower_query.startswith("open app") or lower_query.startswith("close app"):
            try:
                parts = query.split()
                action = parts[0].lower()  # "open" or "close"
                
                # Get app name
                app_start = len(f"{action} app ")
                app_end = find_next_command_start(query[app_start:])
                
                if app_end > 0:
                    app_name = query[app_start:app_start + app_end].strip()
                    query = query[app_start + app_end:].strip()
                else:
                    app_name = query[app_start:].strip()
                    query = ""
                
                # Check if it's a website
                website = None
                if "website" in app_name.lower():
                    website_parts = app_name.lower().split("website", 1)
                    if len(website_parts) > 1:
                        app_name = website_parts[0].strip()
                        website = website_parts[1].strip()
                
                result = open_or_close_software(app_name, action, website)
                response = result
            except Exception as e:
                response = f"Error in open/close app command: {e}"
                query = query[len("open app" if lower_query.startswith("open app") else "close app"):].strip()
                
            all_responses.append(response)
            command_found = True
        
        # 29. Delete a tool: "delete tool <tool_name>"
        elif lower_query.startswith("delete tool"):
            tool_start = len("delete tool ")
            tool_end = find_next_command_start(query[tool_start:])
            
            if tool_end > 0:
                tool_name = query[tool_start:tool_start + tool_end].strip()
                query = query[tool_start + tool_end:].strip()
            else:
                tool_name = query[tool_start:].strip()
                query = ""
                
            result = delete_tool(tool_name)
            response = result
            all_responses.append(response)
            command_found = True
        
        # 30. Set an alarm: "set alarm for <time>" (time in 24-hour format, e.g., 18:00)
        elif lower_query.startswith("set alarm"):
            time_start = lower_query.find("for") + 4 if "for" in lower_query else len("set alarm ")
            time_end = find_next_command_start(query[time_start:])
            
            if time_end > 0:
                time_str = query[time_start:time_start + time_end].strip()
                query = query[time_start + time_end:].strip()
            else:
                time_str = query[time_start:].strip()
                query = ""
                
            result = Set_Alarm(time_str)
            response = f"Alarm set for {time_str}. {result}"
            all_responses.append(response)
            command_found = True
        
        # If no command was found in this iteration, exit the loop
        if not command_found:
            break
        
        commands_processed = True
    
    # Combine all responses
    if commands_processed:
        answer = " | ".join(all_responses)
        text_queue.put(answer)
        print(answer, flush=True)
        
        # If there's remaining text that didn't match any commands, mention it
        if query.strip():
            remaining_text = f"I couldn't process: '{query.strip()}'"
            text_queue.put(remaining_text)
            print(remaining_text, flush=True)
        
        return False  # Commands were processed
    
    return True  # No commands were processed, continue with LLM

def find_next_command_start(text):
    """
    Find the position where the next command might start.
    Returns -1 if no new command is found.
    """
    command_keywords = [
        "play ", "download this", "open", "close", "click", "type", "write",
        "enter", "weather in", "run code:", "translate", "convert", "joke",
        "quote", "define", "screenshot", "generate", "lookup", "system info",
        "search file", "ocr image", "scrape website", "set timer", "set alarm"
    ]
    
    positions = []
    for keyword in command_keywords:
        pos = text.lower().find(" " + keyword)
        if pos >= 0:
            positions.append(pos + 1)  # +1 to account for the space
    
    return min(positions) if positions else -1

def remove_command(query, action, keyword):
    """Remove a command from the query string."""
    pattern = f"{action}.*?{keyword}"
    
    # Find where this pattern ends in the query
    match_end = -1
    lower_query = query.lower()
    action_pos = lower_query.find(action.lower())
    
    if action_pos >= 0:
        keyword_pos = lower_query.find(keyword.lower(), action_pos)
        if keyword_pos >= 0:
            match_end = keyword_pos + len(keyword)
    
    if match_end > 0:
        return query[match_end:].strip()
    return query

def remove_site_from_query(query, site_keyword):
    """Remove a specific site reference from the query."""
    lower_query = query.lower()
    site_pos = lower_query.find(site_keyword)
    
    if site_pos >= 0:
        # Check if this is a standalone word by checking spaces before/after
        # or if it's at the beginning/end of the string
        before_ok = (site_pos == 0 or lower_query[site_pos-1].isspace())
        after_pos = site_pos + len(site_keyword)
        after_ok = (after_pos >= len(lower_query) or lower_query[after_pos].isspace())
        
        if before_ok and after_ok:
            # It's a standalone word, so we can remove it
            before_part = query[:site_pos].rstrip()
            after_part = query[after_pos:].lstrip()
            return before_part + (" " if before_part and after_part else "") + after_part
    
    return query

def run(chatmode=False):
    if not chatmode:
        Query = speechrecognition()
    else:
        Query= input('\nAsk: ')
    if Query != '':
        STOP_SPEECH_EVENT.clear()
        HOT_WORD_DECT_IS_ON_EVENT.set()
        threading.Thread(target=clap_detection, daemon=True).start()
        worker = threading.Thread(target=tts_worker, daemon=False)
        worker.start()
        print(f"==> {AI_Name} AI: ",end="")
        generate:bool=filter_queries(Query)
        if generate:
            for chunk in Chat(Query):
                text_queue.put(emoji_pattern.sub('', chunk.replace('*', '')))
                print(chunk, flush=True, end='')
        text_queue.put(None)
        text_queue.join()  # Wait until the TTS worker has processed all chunks.
        worker.join()
        while not global_buffer.empty():
            sleep(0.1)

if __name__ == "__main__":
    while True:
        run()