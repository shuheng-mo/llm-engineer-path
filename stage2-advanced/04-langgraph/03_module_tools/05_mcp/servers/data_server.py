"""MCP Server — Tools 多模态/结构化输出示例

对应课程章节：模块三 / 4.4.1
"""

from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Data")


class UserProfile(BaseModel):
    name: str
    age: int
    email: str


@mcp.tool()
async def get_user_profile(user_id: str) -> dict:
    """获取用户资料（返回结构化数据）"""
    return {
        "text": f"用户 {user_id} 的资料已找到",
        "structured_content": {
            "name": "张三",
            "age": 30,
            "email": "zhangsan@example.com",
        },
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
