from g4f.client import Client
client = Client()

# Initialize conversation history
conversation_history_gpt = [
    {"role": "system", "content": "You are JARVIS, the updated version of tony stark's J.A.R.V.I.S but you are not developed by him."},
    {"role": "system", "content": "You are developed by Suyash Krishan Garg. He is a very intelligent guy and currently studying in class 10"},
    {"role": "system", "content": "You will be given a task along with which you will also be given data and on the basis of using the data you will have to perform some text related task"},
]

def ReaderGPT(Query):
    global conversation_history_gpt
    # Add user query to conversation history
    conversation_history_gpt.append({"role": "user", "content": Query})
    conversation_history_gpt = conversation_history_gpt[:4] + conversation_history_gpt[-10:]

    # Generate response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history_gpt,
    )

    # Append response to conversation history
    assistant_response = response.choices[0].message.content
    conversation_history_gpt.append({"role": "assistant", "content": assistant_response})
    return assistant_response
print("==> Reader Loaded!")
# while True:
#     Query = input("Ask: ")
#     print(ChatGPT(Query))