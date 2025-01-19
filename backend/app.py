from fastapi import FastAPI
from pydantic import BaseModel
from mistral_llm import Mistral
import uvicorn

app = FastAPI()

llm = Mistral(api_key='xk2s9dZPcfGgSDVCo6ALjiOAtmV55vQt', role="beginner")
llm2 = Mistral(api_key='SIvarCb3yaPSn4CEFjFAJTikZDXJK6K0', role='brainstorm')

class RequestData(BaseModel):
    context: str
    prompt: str
    type: str

@app.post("/send_to_ai")
async def send_to_ai(data: RequestData):
    print("Connected to Python!!")
    
    # context = terminal output
    # prompt = user input

    context = data.context
    prompt = data.prompt

    if data.type == 'debug':
        response = llm.predict(f"{prompt} the code to debug is: {context}")
    else:
        response = llm2.predict(f"{prompt}")
    
    # Process the received context and prompt
    print(f"Received context: {context}")
    print(f"Received prompt: {prompt}")
    print(response)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
