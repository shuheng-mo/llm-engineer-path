"""abatch_as_completed — 哪个先完成先返回（保留索引）

对应课程章节：第三章 / 5.4
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


async def batch_as_completed_demo():
    model = init_chat_model(
        "qwen-plus",
        model_provider="openai",
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )

    inputs = ["什么是人工智能", "什么是深度学习", "什么是机器学习"]
    print("开始请求...\n")
    async for index, result in model.abatch_as_completed(inputs):
        print(f"第{index}个问题的结果：")
        print(result.content[:50])
        print("..\n")


if __name__ == "__main__":
    asyncio.run(batch_as_completed_demo())
