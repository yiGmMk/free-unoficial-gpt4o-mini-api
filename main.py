from fastapi import FastAPI
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/chat/")
async def chat(query: str):
    results = None
    try:
        results = DDGS().chat(query, model='gpt-4o-mini')
        return JSONResponse(content={"results": results})
    except Exception as e:
        try:
            results = DDGS().chat(query, model='claude-3-haiku')
            return JSONResponse(content={"results": results})
        except Exception as e:
            return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3211, log_level="info")
