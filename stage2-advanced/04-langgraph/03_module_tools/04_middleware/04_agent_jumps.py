"""Middleware — Agent jumps（提前跳到 end）

对应课程章节：模块三 / 3.3.6
"""

from typing import Any

from langchain.agents.middleware import AgentState, after_model, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime


@after_model
@hook_config(can_jump_to=["end"])
def check_for_blocked(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    last = state["messages"][-1]
    if "BLOCKED" in last.content:
        return {
            "messages": [AIMessage("该请求无法处理，我需要在这里停止。")],
            "jump_to": "end",
        }
    return None
