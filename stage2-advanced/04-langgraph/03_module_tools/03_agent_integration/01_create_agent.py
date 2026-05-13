"""create_agent 标准实现（最简版本）

对应课程章节：模块三 / 2.1.3
"""

import pathlib
import sys
from datetime import datetime

from langchain.agents import create_agent
from langchain.tools import tool

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


agent = create_agent(
    model=model,
    tools=[get_weather, get_time],
    system_prompt="你是一个友好的助手，可以查询天气和时间。",
)


if __name__ == "__main__":
    result = agent.invoke({"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]})
    print(result["messages"][-1].content)
