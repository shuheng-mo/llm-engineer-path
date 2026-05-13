"""create_agent + Checkpointer — 多轮对话短期记忆

对应课程章节：模块三 / 2.3.1
"""

import pathlib
import sys
from datetime import datetime

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天，25°C"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [get_weather, get_time]

memory = MemorySaver()

agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    checkpointer=memory,
)

config = {"configurable": {"thread_id": "user_123"}}

# 第一轮
agent.invoke({"messages": [{"role": "user", "content": "我叫张三"}]}, config=config)

# 第二轮 — Agent 能记住上下文
response = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫什么名字？"}]}, config=config
)
print(response["messages"][-1].content)  # 您叫张三。
