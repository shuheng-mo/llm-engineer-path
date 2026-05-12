"""异步批量调用 model.abatch()

对应课程章节：第三章 / 5.3
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


async def batch_process():
    model = init_chat_model(
        "qwen-max",
        model_provider="openai",
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        temperature=0.7,
    )

    inputs = [
        [HumanMessage(content="什么是人工智能")],
        [HumanMessage(content="什么是机器学习")],
        [HumanMessage(content="什么是深度学习")],
    ]
    responses = await model.abatch(inputs)
    for response in responses:
        print(response.content[:50])


if __name__ == "__main__":
    asyncio.run(batch_process())
