"""流式输出注意事项 — 错误处理 / 收集完整响应 / 超时配置

对应课程章节：第三章 / 4.5
"""

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


# 1. 错误处理
model = init_chat_model(
    "qwen-plus",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

try:
    for chunk in model.stream("请生成一篇长文章"):
        print(chunk.content, end="", flush=True)
except Exception as e:
    print(f"\n流式输出错误: {e}")


# 2. 收集完整响应
full_response = ""
for chunk in model.stream("你好"):
    full_response += chunk.content
    print(chunk.content, end="", flush=True)
print(f"\n\n完整响应: {full_response}")


# 3. 超时
# model_with_timeout = init_chat_model(
#     "qwen-plus", model_provider="openai",
#     timeout=30,        # 30 秒超时
#     streaming=True,
# )
