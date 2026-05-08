"""max_tokens — 限制最大输出长度

对应课程章节：第三章 / 2.4
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

model = init_chat_model(
    "qwen-max", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0.7, max_tokens=500,
)

response = model.invoke("请详细解释量子计算的原理")
print(response.content)
