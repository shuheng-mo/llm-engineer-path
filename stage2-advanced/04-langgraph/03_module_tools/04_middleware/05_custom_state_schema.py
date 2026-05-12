"""Middleware — 自定义 State schema + 计数器

对应课程章节：模块三 / 3.3.7
"""

from typing import Any

from typing_extensions import NotRequired

from langchain.agents.middleware import AgentState, after_model, before_model
from langgraph.runtime import Runtime


class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]


@before_model(state_schema=CustomState, can_jump_to=["end"])
def check_call_limit(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    if state.get("model_call_count", 0) > 10:
        return {"jump_to": "end"}
    return None


@after_model(state_schema=CustomState)
def increment_counter(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}
