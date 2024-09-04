from fastapi import FastAPI
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
    results = None
    try:
        return chat_with_model(query, model='gpt-4o-mini')
    except Exception as e:
        try:
            return chat_with_model(query, model='claude-3-haiku')
        except Exception as e:
            return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3211, log_level="info")
