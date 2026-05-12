"""FastAPI 集成异步流式 — StreamingResponse 直接吐 chunk

对应课程章节：第三章 / 4.3 FastAPI 集成

依赖:
uv pip install fastapi 'uvicorn[standard]'
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chat_models import init_chat_model
from starlette.responses import StreamingResponse

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

app = FastAPI()

model = init_chat_model(
    "qwen-max",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
    temperature=0.7,
)


@app.get("/stream")
async def stream_chat(question: str = "请介绍一下什么是深度学习"):
    async def generate():
        async for chunk in model.astream(question):
            yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
