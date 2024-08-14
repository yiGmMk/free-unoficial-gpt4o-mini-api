from fastapi import FastAPI
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/chat/")
async def chat(query: str):
    results = DDGS().chat(query, model='gpt-4o-mini')
    return JSONResponse(content={"results": results})

