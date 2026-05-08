"""MCP 拦截器 — 在拦截器内访问 Store 做个性化

对应课程章节：模块三 / 4.5.1 示例 2
"""
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.store.memory import InMemoryStore


@dataclass
class Context:
    user_id: str


async def personalize_search(request: MCPToolCallRequest, handler):
    """基于用户偏好个性化搜索"""
    runtime = request.runtime
    user_id = runtime.context.user_id
    store = runtime.store

    prefs = store.get(("preferences",), user_id)

    if prefs and request.name == "search":
        modified_args = {
            **request.args,
            "language": prefs.value.get("language", "zh"),
            "limit": prefs.value.get("result_limit", 10),
        }
        request = request.override(args=modified_args)

    return await handler(request)


# 用法
# client = MultiServerMCPClient({...}, tool_interceptors=[personalize_search])
# agent = create_agent(model, tools, context_schema=Context, store=InMemoryStore())
