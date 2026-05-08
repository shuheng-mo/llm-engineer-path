"""MCP 拦截器 — 基于 state 的权限控制（拦截敏感工具）

对应课程章节：模块三 / 4.5.1 示例 3
"""
from langchain.messages import ToolMessage
from langchain_mcp_adapters.interceptors import MCPToolCallRequest


async def require_authentication(request: MCPToolCallRequest, handler):
    """阻止未认证用户调用敏感工具"""
    runtime = request.runtime
    state = runtime.state
    is_authenticated = state.get("authenticated", False)

    sensitive_tools = ["delete_file", "update_settings", "export_data"]

    if request.name in sensitive_tools and not is_authenticated:
        return ToolMessage(content="需要认证。请先登录。", tool_call_id=runtime.tool_call_id)

    return await handler(request)
