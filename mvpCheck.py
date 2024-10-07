import requests
from langchain.agents import Tool, AgentType
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import requests
import json


from configgg import mistralApi

mistral_model = "open-mistral-7b"

llm = ChatMistralAI(
    model=mistral_model,
    mistral_api_key=mistralApi
)

def search_faiss(query: str) -> str:
    # Define the URL for the GET request
    url = "http://213.219.228.90:8000/search/"

    # Define the headers for the request
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    payload = {
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
            results = data['results']

            if results:
                return "\n".join(results)
            else:
                return "No product information found in the results."
        else:
            return "Unexpected response format from the server."

    except requests.RequestException as e:
        return f"Error: Unable to fetch product information. {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Unable to parse the response. {str(e)}"

faiss_tool = Tool(
    name="ProductInfoSearch",
    func=search_faiss,
    description="Searches for product information in the database using natural language queries."
)

prompt = """You are a helpful assistant focused on providing product information. 
Always use the ProductInfoSearch tool to find information about products. 
If the information is not found or if there's an error, politely inform the user. 
Do not make up information or provide details that are not returned by the tool."""


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    [faiss_tool],
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": prompt,
    }
)

def chatbot():
    print("Hi, I'm your helpful assistant for product information! How can I assist you today?")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Assistant: Thank you for using our product information service. Goodbye!")
            break

        try:
            result = agent.run(input=user_query)
        except Exception as e:
            result = f"I apologize, but I encountered an error while retrieving the product information. Please try again. Error: {str(e)}"

        print(f"Assistant: {result}")

if __name__ == "__main__":
    chatbot()