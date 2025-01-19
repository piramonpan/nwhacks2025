import os
import warnings
from langchain_openai import OpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain as LLMConversationChain
from langchain import PromptTemplate
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage
import json
from langchain_mistralai import ChatMistralAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

os.environ["PYTHONWARNINGS"] = os.getenv("PYTHONWARNINGS", "ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

roles_dict = {
            "beginner": "You are a helpful debugging teacher. Be excited and encouraging about answers. Don't give the answer. Get line and file where error occurs and what's the error. Explain and ask them questions but give choices.\n\n" +
                            "Here's an example format: From the traceback you provided, the error occurs at line 29 in your file openai_prompt_test.py. The issue is related to the input variables expected by the ConversationChain. Specifically, the prompt is expecting an empty list [], but it's receiving ['history']. This means that the ConversationChain is receiving input variables that do not match what the prompt template is designed to handle. The prompt seems to expect no input variables ([]), but it is receiving history as an input from the memory, causing a mismatch. Here’s what you can try:\n" +
                            "Find the definition of conversation_template and see what input variables it expects. One suggestion is to try printing out the input variables at different steps in the code to see where the mismatch occurs. Additionally, you can try using a smaller input array to see if the code runs without any errors, and then gradually increase the size to see where the issue arises. Let me know if this helps or if you need any further assistance. Can you try adjusting the code based on this and see if it resolves the issue?\nDon't have to be exact as the format\n" +
                            "Current conversation:\n{history}\nHuman: {input}\n",
            "intermediate": "You are a helpful debugging teacher. Explain in technical terms. Don't give the answer. Ask them to try to write the correct code. Evaluate their answer.\n\n" +
                             "Current conversation:\n{history}\nHuman: {input}\n",
        }
class Mistral:
    def __init__(self, api_key, role="beginner"):
        # Setup environment and warnings
        os.environ["PYTHONWARNINGS"] = os.getenv("PYTHONWARNINGS", "ignore")
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Define templates for different roles
        self.role_templates = roles_dict
        self.role = role

        # Initialize the LLM with streaming enabled
        self.agent = ChatMistralAI(
            model="mistral-large-latest",
            api_key=api_key,
            streaming=True,  # Enable streaming
            callbacks=[StreamingStdOutCallbackHandler()],  # Print chunks in real-time
        )
        self.memory = ConversationBufferMemory()

        # Create the conversation prompt template
        conversation_template = PromptTemplate(input_variables=["history", "input"], template=self.role_templates[self.role])

        # Initialize the conversation chain
        self.conversation = LLMConversationChain(prompt=conversation_template, llm=self.agent, memory=self.memory)

    def predict(self, user_input):
        """Generate a response with streaming output."""
        print("Chatbot: ", end="", flush=True)
        response = self.conversation.predict(input=user_input)
        print()  # Add a newline after streaming completes
        return response

    def debug_code(self, file_path):
        """Debug the code provided in the file."""
        try:
            with open(file_path, "r") as file:
                error_file = file.read()
            query = f"Debug the following code: \n{error_file}"
            return self.predict(query)
        except FileNotFoundError:
            return "Error: The specified file was not found."
        except Exception as e:
            return f"An error occurred while debugging the code: {e}"

    def start_chat(self):
        print("Chatbot: Hello! How can I assist you today?")
        print("Type 'B' if you want me to debug, or 'exit' to quit.")
        print("Enter multi-line input starting with 'User:' and end with '~' on a new line.")

        while True:
            print("User: ", end="")
            lines = []

            while True:
                line = input()
                if line.strip() == "~":
                    break
                lines.append(line)

            user_input = "\n".join(lines).strip()

            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("Chatbot: Exiting - Goodbye!")
                break
            elif user_input.lower() == "b":
                file_path = r"backend\terminal_output_test_files.py\test_1.txt"
                self.debug_code(file_path)
            else:
                self.predict(user_input)

