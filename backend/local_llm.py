import sys
import os
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler

# File streaming callback to write responses to a file
class FileStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        # Ensure the file is empty at the start
        with open(self.file_path, "w") as f:
            f.write("")

    def on_llm_new_token(self, token: str, **kwargs):
        # Write each token to the file
        with open(self.file_path, "a") as f:
            f.write(token)
            f.flush()  # Ensure the content is immediately written to the file

# Specify the output file
output_file = "assistant_response.txt"
file_streaming_callback = FileStreamingCallbackHandler(file_path=output_file)

# Template for the prompts
template = """<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant<|stop|>"""

prompt = PromptTemplate(
    template=template,
    input_variables=["system_prompt", "user_prompt"],
)

# Custom parser for agent output
class CustomOutputParser(AgentOutputParser):
    def parse(self, agent_output):
        if agent_output.strip().startswith("{"):
            return AgentFinish(return_values={"output": agent_output.strip()}, log="Finished parsing response.")
        else:
            return AgentAction(tool="unknown_tool", tool_input=agent_output, log="Parsed tool response.")

parser = CustomOutputParser()
n_batch = 1024  # Adjust for VRAM usage

llm = LlamaCpp(
    model_path='/Users/junhe/Desktop/nwhacks2025/backend/model/llama2.gguf',
    n_gpu_layers=-1,
    n_batch=n_batch,
    temperature=0.8,
    max_tokens=2048,
    streaming=True,
    callbacks=[file_streaming_callback]  # Use file streaming callback
)

llm_chain = LLMChain(llm=llm, prompt=prompt)

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=parser,
    stop=["<|im_end|>"]
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=[], verbose=False)

system_prompt = "You are a helpful teacher assistant. Respond in a kind and encouraging manner to all statements and questions. When a user asks for help do not directly give them the answer but instead guide them towards the right solution."

print("Interactive Chat with Assistant. Type 'exit' to quit.\n")
while True:
    print("You (multiline input, end with `~`):")
    user_prompt_lines = []
    while True:
        line = input()  # Only capture actual user input
        if line.strip().lower() == "exit":
            print("Exiting chat. Goodbye!")
            exit()
        elif line.strip() == "~":  # Check for `~` as the end of user input
            break
        else:
            user_prompt_lines.append(line)
    
    # Combine all lines into a single user prompt
    user_prompt = "\n".join(user_prompt_lines)
    
    if not user_prompt.strip():  # Skip if the user provided no input
        print("No input detected. Try again.\n")
        continue
    
    try:
        # Process the user input and get the assistant's response
        agent_executor.run({'system_prompt': system_prompt, 'user_prompt': user_prompt})
        print(f"Response is being streamed to {output_file}.\n")
    except Exception as e:
        print(f"Error: {e}")