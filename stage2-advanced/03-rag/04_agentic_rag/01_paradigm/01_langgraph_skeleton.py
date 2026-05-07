"""Agentic 思维 — LangGraph 最小骨架（Agent + ToolNode + 循环）

对应课程章节：四 / 第一章 4.3.2
"""
from typing import Literal

from langchain_core.messages import BaseMessage  # noqa: F401
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode  # noqa: F401
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: list[BaseMessage]
    query: str


def agent_reasoning_node(state: AgentState):
    """Agent 节点：负责思考。生成回复，并可能输出 tool_calls 决定是否查资料。"""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)  # noqa: F821
    return {"messages": [response]}


def retrieve_node(state: AgentState):
    """工具节点：通常用预置 ToolNode；这里手写演示原理。"""
    print("--- 执行检索动作 ---")
    return {"messages": ["检索到的上下文信息..."]}


def should_continue(state: AgentState) -> Literal["retrieve", "end"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "retrieve"
    return "end"


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_reasoning_node)
workflow.add_node("retrieve", retrieve_node)
workflow.set_entry_point("agent")
# 关键：从 retrieve 回到 agent 形成循环（自我修正能力的来源）
workflow.add_edge("retrieve", "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"retrieve": "retrieve", "end": END},
)

app = workflow.compile()
