"""seed — 设置随机种子让多次调用结果稳定

对应课程章节：第三章 / 2.5
"""

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

model = init_chat_model(
    "qwen-max",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
    temperature=0.7,
    seed=42,
)

response1 = model.invoke("讲一个关于程序员的笑话")
response2 = model.invoke("讲一个关于程序员的笑话")

print(response1.content)
print(response2.content)
