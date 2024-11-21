from fastapi import FastAPI
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# {
#     "id": "chatcmpl-123",
#     "object": "chat.completion",
#     "created": 1677652288,
#     "choices": [
#         {
#             "index": 0,
#             "message": {
#                 "role": "assistant",
#                 "content": "\n\nHello there, how may I assist you today?"
#             },
#             "finish_reason": "stop"
#         }
#     ],
#     "usage": {
#         "prompt_tokens": 9,
#         "completion_tokens": 12,
#         "total_tokens": 21
#     }
# }
def chat_with_model(query: str, model: str) -> JSONResponse:
    results = None
    try:
        results = DDGS().chat(query, model=model)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    # 假设 results 是一个字符串，需要转换为 OpenAI 标准的 message 格式
    message = {
        "role": "assistant",
        "content": results
    }

    return JSONResponse(content={
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": int(time.time()),
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": len(results.split()),
            "total_tokens": len(results.split())
        }
    })


# 流式响应
stream_response_headers = {
    "Content-Type": "application/octet-stream",
    "Cache-Control": "no-cache",
}


def chat_with_model_stream(query: str, model: str) -> StreamingResponse:
    results = None
    try:
        results = DDGS().chat(query, model=model)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    def stream(msg: str):
        yield msg
    return StreamingResponse(stream(results), headers=stream_response_headers, media_type="text/event-stream")


@app.get("/chat/")
async def chat(query: str) -> JSONResponse:
    try:
        return chat_with_model(query, model="gpt-4o-mini")
    except Exception as e:
        try:
            return chat_with_model(query, model="claude-3-haiku")
        except Exception as e:
            return JSONResponse(content={"error": str(e)})


@app.get("/search/", summary="文本搜索")
async def search(query: str) -> JSONResponse:
    try:
        return JSONResponse(DDGS().text(keywords=query, region="zh-cn"))
    except Exception as e:
        return JSONResponse(content={"error": str(e)})


@app.get("/news/", summary="新闻搜索")
async def search(query: str) -> JSONResponse:
    try:
        return JSONResponse(DDGS().news(keywords=query, region="zh-cn"))
    except Exception as e:
        return JSONResponse(content={"error": str(e)})


@app.get("/suggestions/", summary="搜索建议")
async def search(query: str) -> JSONResponse:
    try:
        return JSONResponse(DDGS().suggestions(keywords=query, region="zh-cn"))
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

    def get_joined_messages(self) -> str:
        # 使用空格或其他分隔符将所有messages中的content连接起来
        return ' '.join(message.content for message in self.messages)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if len(request.messages) == 0:
        return JSONResponse(content={"error": "No messages provided"}, status_code=400)
    if request.model not in ["gpt-4o-mini", "claude-3-haiku", "llama-3-70b", "mixtral-8x7b"]:
        request.model = "gpt-4o-mini"
    msg = request.get_joined_messages()
    try:
        if request.stream:
            return chat_with_model_stream(msg, model=request.model)
        return chat_with_model(msg, model=request.model)
    except Exception as e:
        try:
            if request.stream:
                return chat_with_model_stream(msg, model="claude-3-haiku")
            return chat_with_model(msg, model="claude-3-haiku")
        except Exception as e:
            return JSONResponse(content={"error": str(e)})


@app.get("/v1/models")
def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt4o-mini",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
            {
                "id": "claude-3-haiku",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
            {
                "id": "gpt3.5",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai",
            },
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3211, log_level="info")
