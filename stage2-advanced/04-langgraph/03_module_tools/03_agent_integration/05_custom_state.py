"""扩展 AgentState — 通过 state_schema 或 Middleware 添加自定义字段

对应课程章节：模块三 / 2.3.2
"""

import pathlib
import sys

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from typing_extensions import NotRequired

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model, get_time, get_weather  # noqa: E402

model = get_chat_model("qwen-max")

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
