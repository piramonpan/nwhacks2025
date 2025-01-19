from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class RequestData(BaseModel):
    context: str
    prompt: str

@app.post("/send_to_ai")
async def send_to_ai(data: RequestData):
    print("Connected to Python!!")

    context = data.context
    prompt = data.prompt
    
    # Process the received context and prompt
    print(f"Received context: {context}")
    print(f"Received prompt: {prompt}")
    return {"response": "AI response here"}
    
    return {"response": "AI response here"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
