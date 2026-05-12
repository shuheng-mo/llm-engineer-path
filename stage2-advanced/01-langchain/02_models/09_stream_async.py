"""异步流式输出 — model.astream()，FastAPI 等异步场景

对应课程章节：第三章 / 4.3
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


async def stream_response():
    model = init_chat_model(
        "qwen-max",
        model_provider="openai",
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        temperature=0.7,
    )
    async for chunk in model.astream("请介绍一下 Python 的异步编程"):
        print(chunk.content, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(stream_response())
