"""传统 LLM Completion API（OpenAI SDK 直连，DashScope 兼容模式）

对应课程章节：第三章 / 1.2
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.completions.create(model="qwen-plus", prompt="你是谁？")
print(response.choices[0].text)
