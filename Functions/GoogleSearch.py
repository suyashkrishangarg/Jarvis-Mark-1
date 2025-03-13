import sys
import os
current_dir=os.getcwd()
sys.path.append(current_dir)
import requests as rq
from bs4 import BeautifulSoup
from API_keys import groq2
from googlesearch import search
from groq import Groq
from time import time as t
import threading
requests=rq.Session()
client = Groq(api_key=groq2,)


messages = [
    {"role": "system", "content": "You are a google search query generaror and generates a most relevant query according to the prompt given"},
    {"role": "system", "content": "Now generate a google search query based on the prompt and don't mention date and only output query, nothing else:"},
]

def Llama_8b(Query):
    global response, messages
    messages.append({"role": "user", "content": Query},)
    messages = messages[:2] + messages[-6:]
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.7,
        max_tokens=20,
        top_p=0.95,
        stop=None,
        )
    res=response.choices[0].message.content
    print("==> Searching Query: "+res)
    assistant_response = res
    messages.append({"role": "assistant", "content": assistant_response})
    return assistant_response

def website_info(url,title=False, paragraphs=False, headings=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        # print(f"Searching url: {url}")
        title = soup.title.string if soup.title else "No title found"
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        if title:
            return str(title)
        elif headings:
            return str(headings)
        elif paragraphs:
            return str(paragraphs)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {e}")
        return None

def google_search(search_term, AdvWebSearch=False, num=2, q_generator=False) -> str:
    search_term = search_term.replace('jarvis', '')
    search_term = search_term.removeprefix('search')
    search_term = search_term.removeprefix('for')
    if q_generator:
        search_term=Llama_8b(search_term)
    else:
        print(f"Searching About: {search_term}")
    try:
        response = search(search_term, safe=None, advanced=True, num_results=num)

        formatted_results = []
        links = []
        for result in response:
            title = result.title
            link = result.url
            snippet = result.description
            formatted_result = f"{title}\n{snippet}"
            formatted_results.append(formatted_result)
            links.append(link)

        if AdvWebSearch:
            return "\n".join(links)
        else:
            return "\n".join(formatted_results)
    except Exception as e:
        print(f"Error: {e}")
        return ""

def Reader(url):
    global res
    print(f"Searching url: {url}")
    response = requests.get("https://r.jina.ai/"+url)
    res = response.text
    return(res)

def Reader2(url):
    global res2
    print(f"Searching url: {url}")
    response = requests.get("https://r.jina.ai/"+url)
    res2 = response.text
    return(res2)

def Perplexity_search(search_term, num=2):
    links = google_search(search_term, AdvWebSearch=True, num=num)
    d = []
    for link in links.split("\n"):
        data = Reader(link)
        d.append(data)
    return "\n".join(d)

def Search(search_term):
    links = google_search(search_term, AdvWebSearch=True, num=2)
    link=links.split("\n")
    link1=link[0]
    link2=link[1]
    d=[]
    first= threading.Thread(target=Reader, args=[link1])
    second= threading.Thread(target=Reader2, args=[link2])
    first.start()
    second.start()
    while True:
        if first.is_alive()==False:
            d.append(res)
            second.join()
            d.append(res2)
            break
        elif second.is_alive()==False:
            d.append(res2)
            first.join()
            d.append(res)
            break
    return "\n".join(d)
    
def Search_Only_1_website(search_term):
    links = google_search(search_term, AdvWebSearch=True,num=2)
    link=links.split("\n")
    link1=link[0]
    first= threading.Thread(target=Reader, args=[link1])
    first.start()
    first.join()
    return res

def Ultimate_Search(search_term, num):
    links = google_search(search_term, AdvWebSearch=True, num=num)
    d = []
    for link in links.split("\n"):
        data = Reader(link)
        d.append(data)
    return "\n".join(d)

if __name__=="__main__":
    while True:
        L=t()
        print(google_search("who is elon musk"))
        print(t()-L)
        break