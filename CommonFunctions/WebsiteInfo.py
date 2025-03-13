import requests
import html2text
import sqlite3
import os
import shutil



def get_latest_url():
    # Get the default Chrome history file path
    history_path = os.path.expanduser(
        r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History")

    # Destination path for the copied history file
    history_db_path = os.path.join(os.getcwd(), "braveHistoryCopy.txt")

    # Copy the Chrome history database to a new location
    shutil.copy2(history_path, history_db_path)

    # Connect to the Chrome history database
    conn = sqlite3.connect(history_db_path)
    cursor = conn.cursor()

    # Execute a query to retrieve the latest URL from the history
    cursor.execute("SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 1")
    latest_url = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Remove the copied history database
    os.remove(history_db_path)


    return latest_url

print(get_latest_url())

def website_info():
    try:
        url = get_latest_url()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        text_content = html2text.html2text(html_content)
        return text_content     
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {e}")

print(website_info())
