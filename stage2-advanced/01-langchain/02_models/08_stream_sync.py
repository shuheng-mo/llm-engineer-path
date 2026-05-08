"""同步流式输出 — model.stream()

对应课程章节：第三章 / 4.2
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
    temperature=0.7,
)

# 基本用法：逐 chunk 输出
for chunk in model.stream("请详细解释一下什么是深度学习？"):
    print(chunk.content, end="", flush=True)

print()

# chunk 对象详解
for chunk in model.stream("你好"):
    print(f"类型: {type(chunk)}")
    print(f"内容: {repr(chunk.content)}")
    print(f"元数据: {chunk.response_metadata}")
    print("---")
