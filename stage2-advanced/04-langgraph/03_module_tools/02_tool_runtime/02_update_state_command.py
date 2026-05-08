"""ToolRuntime — 用 Command 让工具更新 state（含清空 messages）

对应课程章节：模块三 / 1.2.3
"""
from langchain.messages import RemoveMessage
from langchain.tools import ToolRuntime, tool
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import Command


@tool
def clear_conversation() -> Command:
    """清空对话历史"""
    return Command(
        update={"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]},
    )


@tool
def update_user_name(new_name: str, runtime: ToolRuntime) -> Command:
    """更新用户姓名"""
    return Command(update={"user_name": new_name})
