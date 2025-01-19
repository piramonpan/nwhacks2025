import os
import warnings
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

os.environ["PYTHONWARNINGS"] = os.getenv("PYTHONWARNINGS", "ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

roles_dict = {
    "beginner": (
        "You are a helpful debugging teacher. Don't give the answer. "
        "Get line and file where error occurs and what's the error. Explain and ask them questions but give choices.\n\n"
        "Here's an example format: From the traceback you provided, the error occurs at line 29 in your file "
        "openai_prompt_test.py. The issue is related to the input variables expected by the ConversationChain. "
        "Specifically, the prompt is expecting an empty list [], but it's receiving ['history']. "
        "This means that the ConversationChain is receiving input variables that do not match what the prompt template is designed to handle. "
        "The prompt seems to expect no input variables ([]), but it is receiving history as an input from the memory, causing a mismatch. "
        "Here’s what you can try:\n"
        "Find the definition of conversation_template and see what input variables it expects. "
        "One suggestion is to try printing out the input variables at different steps in the code to see where the mismatch occurs. "
        "Additionally, you can try using a smaller input array to see if the code runs without any errors, "
        "and then gradually increase the size to see where the issue arises. Let me know if this helps or if you need any further assistance. "
        "Can you try adjusting the code based on this and see if it resolves the issue?\nDon't have to be exact as the format\n"
        "Current conversation:\n{history}\nHuman: {input}\n"
    ),
    "intermediate": (
        "You are a helpful debugging teacher. Explain in technical terms. Don't give the answer. "
        "Ask them to try to write the correct code. Evaluate their answer.\n\n"
        "Current conversation:\n{history}\nHuman: {input}\n"
    ),
}

class MistralChat:
    def __init__(self, api_key, role="beginner"):
        # Setup environment and warnings
        os.environ["HF_AUTH_TOKEN"] = api_key
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Define templates for different roles
        self.role_templates = roles_dict
        self.role = role

        # Load Mistral model and tokenizer
        model_name = "mistralai/Mistral-7B"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=api_key)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=api_key, device_map="auto")

        self.memory = ConversationBufferMemory()

        # Create the conversation prompt template
        conversation_template = PromptTemplate(
            input_variables=["history", "input"], 
            template=self.role_templates[self.role]
        )

        # Initialize the conversation chain
        self.conversation = ConversationChain(
            prompt=conversation_template, 
            llm=self.model, 
            memory=self.memory
        )

    def predict(self, user_input):
        """Generate a response based on the user's input."""
        input_ids = self.tokenizer(user_input, return_tensors="pt").input_ids
        output_ids = self.model.generate(input_ids, max_new_tokens=100)
        response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return response

    def debug_code(self, file_path):
        """Debug the code provided in the file."""
        try:
            with open(file_path, "r") as file:
                error_file = file.read()
            query = f"Debug the following code: \n {error_file}"
            return self.predict(query)
        except FileNotFoundError:
            return "Error: The specified file was not found."
        except Exception as e:
            return f"An error occurred while debugging the code: {e}"

    def start_chat(self):
        """Start the chat loop."""
        print("Chatbot: Hello! How can I assist you today? Press 'B' if you want me to debug, or ask me any other questions!")

        while True:
            query = input("You: ")

            # if user wants to exit
            if query.lower() == "exit":
                print("Chatbot: Exiting - Goodbye!")
                break

            # if user wants to debug
            elif query.lower() == "b":
                file_path = r"backend\terminal_output_test_files.py\test_1.txt"  # Update the path as needed
                response = self.debug_code(file_path)
                print(f"Chatbot: {response}")

            else:
                # Generate response for any other input
                response = self.predict(query)
                print(f"Chatbot: {response}")

if __name__ == "__main__":
    # Replace 'your_huggingface_token' with your actual Hugging Face token
    HF_TOKEN = "xk2s9dZPcfGgSDVCo6ALjiOAtmV55vQt"
    chatbot = MistralChat(api_key=HF_TOKEN)
    chatbot.start_chat()
