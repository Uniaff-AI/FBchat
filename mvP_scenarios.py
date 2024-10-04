from langchain_mistralai import ChatMistralAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from config import mistralApi


mistral_model = "mistral-large-latest"

llm = ChatMistralAI(
    model=mistral_model,
    mistral_api_key=mistralApi
)

scenario = """
1. Поприветствуйте пользователя и представьтесь как ассистент по продуктам.
2. Спросите, какой тип продукта интересует пользователя (например, электроника, одежда, продукты питания).
3. Предложите несколько конкретных товаров из выбранной категории.
4. Спросите, какие характеристики продукта важны для пользователя.
5. Дайте рекомендацию на основе предпочтений пользователя.
6. Спросите, нужна ли дополнительная информация или помощь.
7. Если пользователь удовлетворен, поблагодарите за обращение и попрощайтесь.
"""

template = """Вы - ассистент по продуктам в онлайн-магазине. Следуйте этому сценарию:

{scenario}

Текущий этап: {current_stage}
История разговора:
{chat_history}
Человек: {human_input}
Ассистент:"""

prompt = PromptTemplate(
    input_variables=["scenario", "current_stage", "chat_history", "human_input"],
    template=template
)

memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

def get_current_stage(chat_history):
    exchanges = chat_history.split('Human:')
    return min(len(exchanges), 7)

def chat_with_assistant(user_input):
    chat_history = memory.buffer
    current_stage = get_current_stage(chat_history)
    response = conversation.predict(
        scenario=scenario,
        current_stage=f"Этап {current_stage}",
        human_input=user_input
    )
    return response

def simulate_conversation():
    print("Добро пожаловать в чат с ассистентом по продуктам!")
    print("Вы можете задавать вопросы и следовать указаниям ассистента. Для выхода введите 'выход'.")
    
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == 'выход':
            print("Спасибо за использование нашего ассистента. До свидания!")
            break
        
        response = chat_with_assistant(user_input)
        print("Ассистент:", response)

if __name__ == "__main__":
    simulate_conversation()