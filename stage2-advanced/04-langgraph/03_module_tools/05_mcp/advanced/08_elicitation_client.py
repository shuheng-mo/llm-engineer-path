"""MCP 客户端 — 处理 Elicitation 请求

对应课程章节：模块三 / 4.5.4 客户端处理
"""
from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult


async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """实际应用中应根据 params.message / params.requestedSchema 提示用户输入。"""
    return ElicitResult(action="accept", content={"email": "user@example.com", "age": 25})


client = MultiServerMCPClient({}, callbacks=Callbacks(on_elicitation=on_elicitation))
