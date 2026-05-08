"""MCP 日志记录（Logging）

对应课程章节：模块三 / 4.5.3
"""
from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.types import LoggingMessageNotificationParams


async def on_logging_message(params: LoggingMessageNotificationParams, context: CallbackContext):
    print(f"[{context.server_name}] {params.level}: {params.data}")


client = MultiServerMCPClient({}, callbacks=Callbacks(on_logging_message=on_logging_message))
