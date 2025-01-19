import os
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import LlamaCpp
from langchain.callbacks.base import BaseCallbackHandler

# File streaming callback to write responses to a file
class FileStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        with open(self.file_path, "w") as f:
            f.write("")

    def on_llm_new_token(self, token: str, **kwargs):
        with open(self.file_path, "a") as f:
            f.write(token)
            f.flush()

# File streaming setup
output_file = "assistant_response.txt"
file_streaming_callback = FileStreamingCallbackHandler(file_path=output_file)

# Memory for conversation
memory = ConversationBufferMemory()

# LlamaCpp model configuration
llm = LlamaCpp(
    model_path='/Users/junhe/Desktop/nwhacks2025/backend/model/meta.gguf',
    n_gpu_layers=-1,
    n_batch=1024,
    temperature=0.8,
    max_tokens=2048,
    context_length=2048,
    n_ctx=4096,
    streaming=True,
    callbacks=[file_streaming_callback]
)

# Debugging teacher prompt template
ROLE_BEGINNER_TEACHER = (
    "You are a helpful debugging teacher. Don't give the answer. "
    "Identify the line and file where the error occurs and explain it. "
    "Ask the user to correct it themselves. "
    "Current conversation:\n{history}\nHuman: {input}\n"
)

# Teacher assistant prompt template
ROLE_TEACHER_ASSISTANT = (
    "You are a helpful teacher assistant. Respond in a kind and encouraging manner to all statements and questions. "
    "Do not directly give the answer but guide the user towards the solution. "
    "Current conversation:\n{history}\nHuman: {input}\n"
)

# Debugging Conversation Chain
debugging_chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=PromptTemplate(
        template=ROLE_BEGINNER_TEACHER,
        input_variables=["history", "input"]
    )
)

# General Assistant Chain
general_chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=PromptTemplate(
        template=ROLE_TEACHER_ASSISTANT,
        input_variables=["history", "input"]
    )
)

# Main loop
print("Chatbot: Hello! How can I assist you today? Type 'debug' for debugging assistance, or ask any other question.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    elif user_input.lower() == "debug":
        error_file_path = '/Users/junhe/Desktop/nwhacks2025/backend/terminal_output_test_files.py/full_error.txt'
        with open(error_file_path, "r") as file:
            error_content = file.read()
        query = f"Debug the following code:\n{error_content}"
        response = debugging_chain.run(input=query)
    else:
        response = general_chain.run(input=user_input)
    
    # Terminate at the second occurrence of "Assistant:"
    if response.count("Assistant:") > 1:
        response = response.split("Assistant:", 1)[0].strip()

    print(f"Chatbot: {response}")
    memory.chat_memory.add_user_message(user_input)
    memory.chat_memory.add_ai_message(response)
