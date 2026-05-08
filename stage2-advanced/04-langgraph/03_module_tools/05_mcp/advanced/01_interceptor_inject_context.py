"""MCP 拦截器 — 把用户上下文注入到工具调用

对应课程章节：模块三 / 4.5.1 示例 1
"""
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest


@dataclass
class Context:
    user_id: str
    api_key: str


async def inject_user_context(request: MCPToolCallRequest, handler):
    """将用户凭证注入到工具调用中"""
    runtime = request.runtime
    user_id = runtime.context.user_id

    modified_request = request.override(args={**request.args, "user_id": user_id})
    return await handler(modified_request)


# 用法
# client = MultiServerMCPClient({...}, tool_interceptors=[inject_user_context])
# tools = await client.get_tools()
# agent = create_agent(model, tools, context_schema=Context)
# result = await agent.ainvoke(
#     {"messages": [{"role": "user", "content": "查询我的订单"}]},
#     context={"user_id": "user_123", "api_key": "sk-..."},
# )
