"""扩展 AgentState — 通过 state_schema 或 Middleware 添加自定义字段

对应课程章节：模块三 / 2.3.2
"""

from typing_extensions import NotRequired

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware


class CustomState(AgentState):
    user_preferences: NotRequired[dict]
    task_count: NotRequired[int]


# 方式 1：通过 state_schema
agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    state_schema=CustomState,
)


# 方式 2：通过 Middleware（推荐）
class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime):
        # 这里可访问 state["user_preferences"]
        return None


agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    middleware=[CustomMiddleware()],
)
