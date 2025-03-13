import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import colorama
# Add current directory to path
current_dir = os.getcwd()
sys.path.append(current_dir)
from Frontend.GUI import ShowTextToScreen  # import GUI updater
colorama.init(autoreset=True)

# Configure Chrome options to reduce logging output.
chrome_options = webdriver.ChromeOptions()
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument("--enable-tcp-caching")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Redirect service logs to os.devnull to hide them.
service = Service(ChromeDriverManager().install(), log_path=os.devnull)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Set the website URL (local file or remote URL)
website = f"{current_dir}\\CommonFunctions\\Listen.html"
# Alternatively:
# website = "https://663381dffa96bfc03108fa69--genuine-duckanoo-f5df47.netlify.app/"
driver.get(website)

def speechrecognition(Print=True):
    driver.get(website)
    driver.find_element(by=By.ID, value='start').click()
    if Print:
        print(colorama.Fore.MAGENTA + "\nListening...")
    final_text = ""
    previous_text = ""
    if Print:
        print(colorama.Fore.GREEN + "==> You Said: ", end="")
    # Stream recognized text live:
    while True:
        text = driver.find_element(by=By.ID, value='output').text
        new_part = text[len(previous_text):]
        if new_part:
            final_text += new_part
            # Update the GUI file with the live query:
            current_text = f"You : {final_text}"
            ShowTextToScreen(current_text)
            if Print:
                print(colorama.Fore.LIGHTGREEN_EX + new_part, end="", flush=True)
        previous_text = text
        if "<ended>" in text:
            break
    return final_text.lower()


print("==> Speech Recognition Loaded!")

if __name__ == "__main__":
    while True:
        speechrecognition()

