import pandas as pd
import requests
from langchain.docstore.document import Document
from langchain_community.document_transformers import Html2TextTransformer
from mistralai import Mistral
from configgg import mistralApi
import os
import psutil
import asyncio
import websockets
import json
from mistralai import Mistral
from configgg import mistralApi

client = Mistral(api_key=mistralApi)
df = pd.read_excel('coin_urls.xlsx')
df = df.head(10)

html2text = Html2TextTransformer()

docs = []

def check_memory():
    memory = psutil.virtual_memory()
    return memory.percent >90


def extract_text_from_url(url):
    """Extract text from a single URL"""
    try:
        if check_memory():
            raise MemoryError("Memory usage is too high")

        response = requests.get(url, timeout=10)
        html_content = response.text
        doc = Document(page_content=html_content, metadata={"source": url})

        print(f"\n--- Extracted text from {url} ---\n")
        print(html_content[:500] + '...' if len(html_content) > 500 else html_content)
        print("\n--- End of extracted text ---\n")

        return doc
    except requests.exceptions.RequestException as e:
        print(f"Error extracting text from {url}: {e}")
        return None
    except MemoryError as e:
        print(f"Memory error while processing {url}: {e}")
        return None


# Function to fetch HTML and convert to text using Html2TextTransformer
def extract_text_via_html2text(urls):
    for url in urls:
        try:
            response = requests.get(url)
            html_content = response.text
            docs.append(Document(page_content=html_content, metadata={"source": url}))

            print(f"\n--- Extracted text from {url} ---\n")
            print(html_content[:500] + '...' if len(html_content) > 500 else html_content)
            print("\n--- End of extracted text ---\n")

        except requests.exceptions.RequestException as e:
            print(f"Error extracting text from {url}: {e}")

    return html2text.transform_documents(docs)

urls = [row['coin url'].replace('{utm_source}', 'example_source') for _, row in df.iterrows()]
docs_transformed = extract_text_via_html2text(urls)

combined_context = ""
for idx, row in df.iterrows():
    extracted_text = docs_transformed[idx].page_content
    print(f"\n--- Transformed text from {row['coin url']} ---\n")
    print(extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text)
    print("\n--- End of transformed text ---\n")

    # Add indicator for which URL the content was taken from
    context_part = f"Source: {row['coin url']}\nOffer: {row['offer']}\nExtracted text (in Hindi):\n\n{extracted_text[:500]}...\n\n"
    combined_context += context_part

prompt = f"""
You are a multilingual assistant specializing in diabetic products. The following information was extracted from various websites, and some of it may be in Hindi:
{combined_context}

Your task:
1. Use the extracted content to answer user queries about diabetic products.
2. Users may ask questions in different languages. Respond in the same language as the user's query.
3. Do not mention translation or language detection in your responses.
4. Provide concise and relevant information based on the extracted content.
5. If the information is not available in the extracted content, politely inform the user that you don't have that specific information.
"""
async def chatbot(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            user_query = data['message']

            if user_query.lower() in ['exit', 'quit', 'bye']:
                await websocket.send(json.dumps({"message": "Thanks for using the service!"}))
                return

            try:
                chat_resp = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_query}
                    ]
                )

                resp_content = chat_resp.choices[0].message.content
                await websocket.send(json.dumps({"message": resp_content}))
            except Exception as e:
                await websocket.send(json.dumps({"message": f"Error: {str(e)}"}))
    except websockets.exceptions.ConnectionClosed:
        pass

async def main():
    server = await websockets.serve(chatbot, "localhost", 8000)
    print("WebSocket server started on ws://localhost:8000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())