"""bind_tools — 把工具直接绑定到模型（让模型自己决策）

对应课程章节：第八章 / 3.2.1
"""
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)


@tool
def add(a: int, b: int) -> int:
    """将两个整数相加。"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """将两个整数相乘。"""
    return a * b


tools = [add, multiply]
llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke("计算 3 加 5 的结果")
print(response)
print(f"Tool Calls: {response.tool_calls}")
