from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler

class StreamingCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end="", flush=True)

template = """<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant"""

prompt = PromptTemplate(
    template=template,
    input_variables=["system_prompt", "user_prompt"],
)

class CustomOutputParser(AgentOutputParser):
    def parse(self, agent_output):
        if agent_output.strip().startswith("{"):
            return AgentFinish(return_values={"output": agent_output.strip()}, log="Finished parsing response.")
        else:
            return AgentAction(tool="unknown_tool", tool_input=agent_output, log="Parsed tool response.")

parser = CustomOutputParser()
n_batch = 1024 # Increase to increase VRAM usage / computation speed, decrease for vice versa

streaming_callback = StreamingCallbackHandler()

llm = LlamaCpp(
    model_path='/Users/junhe/Desktop/nwhacks2025/backend/model/starchat2-15b-v0.1-Q3_K_L.gguf',
    n_gpu_layers=-1,
    n_batch=n_batch,
    temperature=0.8,
    streaming=True,
    callbacks=[streaming_callback]
)

llm_chain = LLMChain(llm=llm, prompt=prompt)

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=parser,
    stop=["<|im_end|>"]
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=[], verbose=True)

system_prompt = "You are a helpful teacher assistant. Respond in a kind and encouraging manner to all statements and questions. When a user asks for help do not directly give them the answer but instead guide them towards the right solution. Always answer in .json format."

print("Interactive Chat with Assistant. Type 'exit' to quit.\n")
while True:
    user_prompt = input("You: ")
    if user_prompt.lower() == "exit":
        print("Exiting chat. Goodbye!")
        break
    
    try:
        result = agent_executor.run({'system_prompt': system_prompt, 'user_prompt': user_prompt})
        print(f"Assistant: {result}\n")
    except Exception as e:
        print(f"Error: {e}")
