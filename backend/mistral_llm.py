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
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document

os.environ["PYTHONWARNINGS"] = os.getenv("PYTHONWARNINGS", "ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

beginner_markdown = "/Users/junhe/Desktop/nwhacks2025/backend/BEGINNER.md"
loader = UnstructuredMarkdownLoader(beginner_markdown)
data = loader.load()
beginner_content = data[0].page_content
intermediate_markdown = "/Users/junhe/Desktop/nwhacks2025/backend/INTERMEDIATE.md"
loader2 = UnstructuredMarkdownLoader(intermediate_markdown)
data2 = loader2.load()
intermediate_content = data2[0].page_content
brainstorm_markdown = "/Users/junhe/Desktop/nwhacks2025/backend/BRAINSTORM.md"
loader = UnstructuredMarkdownLoader(brainstorm_markdown)
data = loader.load()
brainstorm_content = data[0].page_content

roles_dict = {
            "beginner": beginner_content,
            "intermediate": intermediate_content,
            "brainstorm": brainstorm_content,
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

if __name__ == "__main__":
    llm = Mistral(api_key='xk2s9dZPcfGgSDVCo6ALjiOAtmV55vQt')
    llm.start_chat()