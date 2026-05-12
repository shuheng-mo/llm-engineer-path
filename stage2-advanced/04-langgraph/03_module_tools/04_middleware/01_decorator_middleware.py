"""Middleware — @before_model / @after_model 装饰器（简单场景）

对应课程章节：模块三 / 3.3.1
"""

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model, before_model
from langgraph.runtime import Runtime


@before_model(can_jump_to=["end"])
def safety_check(state: AgentState, runtime: Runtime) -> dict | None:
    """安全检查：对话长度限制"""
    if len(state["messages"]) >= 20:
        return {
            "messages": [{"role": "assistant", "content": "对话已达上限"}],
            "jump_to": "end",
        }
    return None


@after_model
def log_response(state: AgentState, runtime: Runtime) -> dict | None:
    """记录模型响应"""
    print(f"模型返回: {state['messages'][-1].content}")
    return None


agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    middleware=[safety_check, log_response],
)
