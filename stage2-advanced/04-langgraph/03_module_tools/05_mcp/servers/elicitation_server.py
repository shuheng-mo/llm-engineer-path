"""MCP Server — Elicitation 交互式输入

对应课程章节：模块三 / 4.5.4
"""

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

server = FastMCP("Profile")


class UserDetails(BaseModel):
    email: str
    age: int


@server.tool()
async def create_profile(name: str, ctx: Context) -> str:
    """创建用户资料，通过 elicitation 请求详细信息"""
    result = await ctx.elicit(message=f"请提供 {name} 的详细信息：", schema=UserDetails)
    if result.action == "accept" and result.data:
        return f"为 {name} 创建资料: email={result.data.email}, age={result.data.age}"
    if result.action == "decline":
        return f"用户拒绝。为 {name} 创建了最小资料。"
    return "资料创建已取消。"


if __name__ == "__main__":
    server.run(transport="http")
