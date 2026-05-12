"""ChatModel — init_chat_model 统一入口（OpenAI 协议接 DashScope）

对应课程章节：第三章 / 1.3
"""

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

llm = init_chat_model(
    "qwen-max",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
    temperature=0.7,
)

messages = [
    SystemMessage(content="你是一个专业的 Python 编程导师，请你用简单易懂的方式回答问题"),
    HumanMessage(content="什么是列表，请举例说明"),
]

response = llm.invoke(messages)
print(response.content)
