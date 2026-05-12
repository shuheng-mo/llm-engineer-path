"""MCP Server — Resources（参数化路径）

对应课程章节：模块三 / 4.4.2
"""

from fastmcp import FastMCP

mcp = FastMCP("Files")


@mcp.resource("config://app.json")
async def get_config() -> str:
    """返回配置文件"""
    return '{"version": "1.0", "debug": true}'


@mcp.resource("docs://{category}/{filename}")
async def get_document(category: str, filename: str) -> str:
    """参数化资源路径"""
    return f"文档内容：{category}/{filename}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
