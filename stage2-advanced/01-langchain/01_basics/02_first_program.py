"""第一个 LangChain 程序 — ChatTongyi 简单调用 + 消息对象 + 响应详情

对应课程章节：第二章 / 6.2
"""
import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

# Step 1：加载环境变量
load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")
print("环境变量加载成功")


# Step 2：初始化模型
model = ChatTongyi(
    model="qwen-plus",          # qwen-turbo / qwen-plus / qwen-max
    temperature=0.7,
    # max_tokens=1000,
)
print("模型初始化成功（qwen-plus）")


# Step 3：构造消息并调用
print("\n" + "=" * 50)
print("【方式一】简单字符串调用")
print("=" * 50)
response = model.invoke("你好！请用一句话介绍一下你自己。")
print(f"模型响应：{response.content}")


print("\n" + "=" * 50)
print("【方式二】使用消息对象")
print("=" * 50)
messages = [
    SystemMessage(content="你是一个友好的 AI 助手，擅长用简洁的语言解释技术概念。"),
    HumanMessage(content="什么是 LangChain？请用 2-3 句话解释。"),
]
response = model.invoke(messages)
print(f"模型响应：{response.content}")


# Step 4：查看响应详情
print("\n" + "=" * 50)
print("【响应详情】")
print("=" * 50)
print(f"响应类型：{type(response)}")
print(f"响应内容：{response.content}")
print(f"响应元数据：{response.response_metadata}")
