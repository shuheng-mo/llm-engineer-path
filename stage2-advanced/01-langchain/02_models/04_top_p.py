"""top_p（核采样）对比 — 通常和 temperature 二选一

对应课程章节：第三章 / 2.3
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

precise_model = init_chat_model(
    "qwen-max", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    top_p=0,
)

creative_model = init_chat_model(
    "qwen-max", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    top_p=0.9,
)

prompt = "请用一个有趣的比喻来描述人工智能"
print("top_p=0:", precise_model.invoke(prompt).content)
print("top_p=0.9:", creative_model.invoke(prompt).content)

# 最佳实践：通常只调整 temperature 或 top_p 其中之一，避免同时调整。
