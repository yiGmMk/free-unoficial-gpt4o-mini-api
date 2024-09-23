from fastapi import FastAPI
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional,List

app = FastAPI()
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def chat_with_model(query: str, model: str) -> JSONResponse:
    results = None
    try:
        results = DDGS().chat(query, model=model)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    return JSONResponse(content={"results": results})

@app.get("/chat/")
async def chat(query: str) -> JSONResponse:
    try:
        return chat_with_model(query, model='gpt-4o-mini')
    except Exception as e:
        try:
            return chat_with_model(query, model='claude-3-haiku')
        except Exception as e:
            return JSONResponse(content={"error": str(e)})

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if len(request.messages) == 0:
        return JSONResponse(content={"error": "No messages provided"}, status_code=400)
    msg=str.join(request.messages,",")
    try:
        return chat_with_model(msg, model=request.model)
    except Exception as e:
        try:
            return chat_with_model(msg, model='claude-3-haiku')
        except Exception as e:
            return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3211, log_level="info")
