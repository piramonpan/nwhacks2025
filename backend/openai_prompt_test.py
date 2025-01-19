from langchain_openai import OpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain, LLMChain
from langchain import PromptTemplate
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage

import warnings
import os

ROLE_BEGINNER_TEACHER = "You are a helpful debugging teacher. Don't give the answer. Get line and file where error occurs and what's the error. Explain and ask them to try to write the correct code. \n Current conversation:\n{history}\nHuman: {input}\n "

## Note: Intermediate teacher is not implemented yet
ROLE_INTERMEDIATE_TEACHER = "You are a helpful debugging teacher. Explain technical terms. Don't give the answer. Ask them to try to write the correct code. Evaluate their answer. \n Current conversation:\n{history}\nHuman: {input}\n "

# os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["PYTHONWARNINGS"] = os.getenv("PYTHONWARNINGS", "ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

agent = OpenAI()

memory = ConversationBufferMemory()

conversation_template = PromptTemplate(input_variables=['history', 'input'], template=ROLE_BEGINNER_TEACHER)
conversation = ConversationChain(prompt=conversation_template, llm=agent, memory=memory)

print("Chatbot: Hello! How can I assist you today? Press B if you want me to debug else ask me any questions!")

while True:
    query = input("You: ")

    # if user want to exit
    if query == "exit":
        print("Chatbot: Exitting - Goodbye!")
        break

    # if user want to debug
    elif query == "B":
        error_file = open(r"backend\terminal_output_test_files.py\start_end_only.txt", "r").read()
        query = f"Debug the following code: \n {error_file}"

    response = conversation.predict(input=query)
    print(f"Chatbot: {response}")
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response)
