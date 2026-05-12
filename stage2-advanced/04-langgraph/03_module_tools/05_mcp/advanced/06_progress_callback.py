"""MCP 进度通知（Progress Notifications）

对应课程章节：模块三 / 4.5.2
"""

from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient


async def on_progress(
    progress: float, total: float | None, message: str | None, context: CallbackContext
):
    percent = (progress / total * 100) if total else progress
    tool_info = f" ({context.tool_name})" if context.tool_name else ""
    print(f"[{context.server_name}{tool_info}] 进度: {percent:.1f}% - {message}")


client = MultiServerMCPClient({}, callbacks=Callbacks(on_progress=on_progress))
