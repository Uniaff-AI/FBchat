import pandas as pd
import requests
from langchain.docstore.document import Document
from langchain_community.document_transformers import Html2TextTransformer
from mistralai import Mistral
from configgg import mistralApi

client = Mistral(api_key=mistralApi)
df = pd.read_excel('coin_urls.xlsx')
df = df.head(10)

html2text = Html2TextTransformer()

docs = []

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
1. Translate the extracted text into English if needed or the language in which you were addressed.
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
