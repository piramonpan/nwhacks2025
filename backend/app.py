from fastapi import FastAPI
from pydantic import BaseModel
from mistral_llm import Mistral
import uvicorn

app = FastAPI()

llm = Mistral(api_key='xk2s9dZPcfGgSDVCo6ALjiOAtmV55vQt')

class RequestData(BaseModel):
    context: str
    prompt: str

@app.post("/send_to_ai")
async def send_to_ai(data: RequestData):
    print("Connected to Python!!")

    context = data.context
    prompt = data.prompt

    response = llm.predict(f"{prompt}")
    print(response)
    
    # Process the received context and prompt
    print(f"Received context: {context}")
    print(f"Received prompt: {prompt}")
    return {f"response: {response}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
