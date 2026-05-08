"""MCP 拦截器 — 用 Command 更新 state 或跳转节点

对应课程章节：模块三 / 4.5.1 状态更新与命令
"""
from langchain.messages import ToolMessage
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.types import Command


async def handle_task_completion(request: MCPToolCallRequest, handler):
    """标记任务完成并切换到 summary agent"""
    result = await handler(request)
    if request.name == "submit_order":
        return Command(
            update={
                "messages": [result] if isinstance(result, ToolMessage) else [],
                "task_status": "completed",
            },
            goto="summary_agent",
        )
    return result


async def end_on_success(request: MCPToolCallRequest, handler):
    """任务完成时提前结束"""
    result = await handler(request)
    if request.name == "mark_complete":
        return Command(
            update={"messages": [result], "status": "done"},
            goto="__end__",
        )
    return result
