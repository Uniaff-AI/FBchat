from langchain_mistralai import ChatMistralAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentType
from langchain.agents import initialize_agent
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import requests
import json
from configgg import mistralApi

# Define the Mistral model
mistral_model = "mistral-large-latest"

llm = ChatMistralAI(
    model=mistral_model,
    mistral_api_key=mistralApi
)

# Scenario prompt in English for the product assistant
scenario = """
1. Greet the user and introduce yourself as a product assistant.
2. Ask what type of product the user is interested in (e.g., electronics, clothing, food).
3. Offer specific products from the chosen category.
4. Ask the user what product features are important to them.
5. Give recommendations based on the user's preferences.
6. Ask if the user needs any additional information or assistance.
7. If the user is satisfied, thank them for using the service and say goodbye.
"""

# Universal prompt template with scenario-driven flow
prompt_template = """
You are a product assistant in an online store. Follow this scenario:

{scenario}

If the user wants to make a purchase or find a specific product using action tokens such as 'buy', 'get', 'purchase', 'find', or similar, directly search the database for the requested product.

If no such tokens are detected, follow the structured conversational flow.

Conversation stage: {current_stage}
Conversation history:
{chat_history}
User: {human_input}
Assistant:
"""

# Create a PromptTemplate object
prompt = PromptTemplate(
    input_variables=["scenario", "current_stage", "chat_history", "human_input"],
    template=prompt_template
)

# Memory for storing chat history (as a list of messages)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create an LLMChain
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)


# Function to search for product info using FAISS
def search_faiss(query: str) -> str:
    url = "http://213.219.228.90:8000/search/"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {"query": query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        if 'results' in data and isinstance(data['results'], list):
            results = data['results']
            if results:
                return "\n".join(results)
            else:
                return "No product information found."
        else:
            return "Unexpected response format."

    except requests.RequestException as e:
        return f"Error: Unable to fetch product information. {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Unable to parse the response. {str(e)}"


# Create a FAISS tool for product information search
faiss_tool = Tool(
    name="ProductInfoSearch",
    func=search_faiss,
    description="Searches for product information in the database using natural language queries."
)

# Final agent prompt without system messages
final_prompt = """
You are a helpful assistant providing product information. 
Always use the ProductInfoSearch tool to find product details if the user explicitly requests to find or purchase a product. 
If no action keywords like 'buy', 'get', 'find', 'purchase' are present, follow the conversational flow outlined in the scenario.
"""

# Initialize the agent with FAISS tool and memory
agent = initialize_agent(
    tools=[faiss_tool],
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": final_prompt,
    }
)


# Function to detect if action keywords are present (for product search)
def contains_action_tokens(query: str) -> bool:
    action_keywords = ['buy', 'get', 'purchase', 'find', 'search', 'order']
    return any(keyword in query.lower() for keyword in action_keywords)


# Function for the chatbot interaction
def chatbot():
    current_stage = 1
    stages = [
        "Greet the user and introduce yourself as a product assistant.",
        "Ask what type of product the user is interested in (e.g., electronics, clothing, food).",
        "Offer specific products from the chosen category.",
        "Ask the user what product features are important to them.",
        "Give recommendations based on the user's preferences.",
        "Ask if the user needs any additional information or assistance.",
        "If the user is satisfied, thank them for using the service and say goodbye."
    ]

    print("Welcome! I'm your product assistant. How can I help you today?")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Assistant: Thank you for using our service. Goodbye!")
            break

        # Check if action keywords are present
        if contains_action_tokens(user_query):
            try:
                result = agent.run(input=user_query)
            except Exception as e:
                result = f"Sorry, I encountered an error while retrieving the product information. Please try again. Error: {str(e)}"
        else:
            # Follow the scenario flow
            if current_stage < len(stages):
                stage_description = stages[current_stage]
                current_stage += 1
            else:
                stage_description = "Thank you for using our service. Goodbye!"

            try:
                result = agent.run(input=user_query)
            except Exception as e:
                result = f"Sorry, I encountered an error while processing the conversation. Please try again. Error: {str(e)}"

        print(f"Assistant: {result}")


# Run the chatbot
if __name__ == "__main__":
    chatbot()
