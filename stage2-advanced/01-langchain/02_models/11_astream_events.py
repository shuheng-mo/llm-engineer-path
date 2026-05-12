"""事件流 astream_events — 区分 model 开始/流式块/结束

对应课程章节：第三章 / 4.4
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


async def stream_events():
    model = init_chat_model(
        "qwen-max",
        model_provider="openai",
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        temperature=0.7,
    )

    async for event in model.astream_events("什么是异步编程?", version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_start":
            print("模型开始生成...")
        elif kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            print(content, end="", flush=True)
        elif kind == "on_chat_model_end":
            print("\n生成完成")


if __name__ == "__main__":
    asyncio.run(stream_events())
