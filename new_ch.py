import requests
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
import requests
from langchain.agents import Tool, AgentType
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from configgg import mistralApi

mistral_model = "open-mistral-7b"



llm = ChatMistralAI(
    model=mistral_model,
    mistral_api_key=mistralApi
)

import requests
import json

def search_faiss(query: str) -> str:
    # Define the URL for the POST request
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
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Check if the response contains results
        if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
            results = data['results']  # Get the results directly

            if results:
                return "\n".join(results)  # Join the results into a single string
            else:
                return "No product information found in the results."
        else:
            return "Unexpected response format from the server."

    except requests.RequestException as e:
        return f"Error: Unable to fetch product information. {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Unable to parse the response. {str(e)}"



# Initialize the FAISS tool
faiss_tool = Tool(
    name="ProductInfoSearch",
    func=search_faiss,
    description="Searches for product information in the database using natural language queries."
)

# Set up the prompt for the assistant
prompt = """You are a helpful assistant focused on providing product information. 
Always use the ProductInfoSearch tool to find information about products. 
If the information is not found or if there's an error, politely inform the user. 
Do not make up information or provide details that are not returned by the tool."""

# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize the agent with the FAISS tool and prompt
agent = initialize_agent(
    [faiss_tool],
    llm,  # Make sure you have the `llm` initialized somewhere in your code
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": prompt,
    }
)

response = search_faiss("diabetic products")
print(response)