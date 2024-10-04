from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import mistralApi

mistral_model = "mistral-large-latest"

llm = ChatMistralAI(
    model=mistral_model,
    mistral_api_key=mistralApi
)

def buy_car(phone_number: str, address: str):
    print(f"Buying a car for phone number {phone_number} at address {address}")
    return "Car purchase completed."

def buy_car_tool(phone_number: str, address: str) -> str:
    """Buys a car for the user given their phone number and address."""
    return buy_car(phone_number, address)

tools = [
    Tool(
        name="BuyCarTool",
        func=buy_car_tool,
        description="Buys a car for the user given their phone number and address."
    )
]

template = """Extract the phone number and address from the user's input for buying a car. 
If the information is not provided, ask the user for the missing details.

User input: {user_input}

Please provide the extracted information in the following format:
Phone number: [extracted phone number]
Address: [extracted address]

If any information is missing, respond with:
Missing information: [list of missing items]
"""

prompt = PromptTemplate(
    input_variables=["user_input"],
    template=template
)

extraction_chain = LLMChain(llm=llm, prompt=prompt)

agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

def main():
    while True:
        user_input = input("Вы: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Extract information using Mistral
        extraction_result = extraction_chain.run(user_input)
        print(f"Извлеченная информация:\n{extraction_result}")
        
        response = agent.run(extraction_result)
        print(f"Бот: {response}")

if __name__ == "__main__":
    main()