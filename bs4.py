import pandas as pd
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral
from configgg import mistralApi

client = Mistral(api_key=mistralApi)

df = pd.read_excel('coin_urls.xlsx')
df = df.head(10)

# Function to extract text from a web page
def extract_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()

        soup = BeautifulSoup(res.content, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])

        print(f"\n--- Extracted text from {url} ---\n")
        print(text[:500] + '...' if len(text) > 500 else text)
        print("\n--- End of extracted text ---\n")

        return text
    except requests.exceptions.RequestException as e:
        print(f"Error extracting text from {url}: {e}")
        return ""

combined_context = ""

# Iterate over each row in DataFrame
for idx, row in df.iterrows():
    url = row['coin url'].replace('{utm_source}', 'example_source')
    text = extract_text(url)

    context_part = f"Offer: {row['offer']}\nExtracted text (in Hindi): {text[:500]}...\n"
    combined_context += context_part


prompt = f"""
You are a multilingual assistant specializing in products. The following information was extracted from various websites, and some of it may be in Hindi:
{combined_context}

Your task:
1. Translate the extracted text into English if needed or the language in which you were adressed.
2. Use the translated content to answer user queries about diabetic products.
3. Users may ask questions in different languages. Translate their questions to English if needed and respond appropriately.
"""


# Chatbot interaction
def chatbot():
    print("Welcome! How can I help you today?")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Assistant: Thanks for using the service!")
            break

        try:
            chat_resp = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_query}
                ]
            )

            resp_content = chat_resp.choices[0].message.content
            print(f"Assistant: {resp_content}")
        except Exception as e:
            print(f"Error in chatbot: {str(e)}")


# Run the chatbot
if __name__ == "__main__":
    chatbot()
