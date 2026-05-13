"""扩展 AgentState — 通过 state_schema 或 Middleware 添加自定义字段

对应课程章节：模块三 / 2.3.2
"""

import pathlib
import sys
from datetime import datetime

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.tools import tool
from typing_extensions import NotRequired

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


class CustomState(AgentState):
    user_preferences: NotRequired[dict]
    task_count: NotRequired[int]


# 方式 1：通过 state_schema
agent = create_agent(
    model=model,
    tools=tools,
    state_schema=CustomState,
)


# 方式 2：通过 Middleware（推荐）
class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime):
        # 这里可访问 state["user_preferences"]
        return None


agent = create_agent(
    model=model,
    tools=tools,
    middleware=[CustomMiddleware()],
)
