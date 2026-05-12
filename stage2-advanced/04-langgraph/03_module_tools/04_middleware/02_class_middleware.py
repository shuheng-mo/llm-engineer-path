"""Middleware — 类方式（复杂场景，推荐工程化写法）

对应课程章节：模块三 / 3.3.2
"""

from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, AgentState
from langgraph.runtime import Runtime


class LoggingMiddleware(AgentMiddleware):
    """统一日志中间件：可复用、可扩展"""

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"[before_model] messages={len(state['messages'])}")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"[after_model] assistant={state['messages'][-1].content}")
        return None


agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    middleware=[LoggingMiddleware()],
)
