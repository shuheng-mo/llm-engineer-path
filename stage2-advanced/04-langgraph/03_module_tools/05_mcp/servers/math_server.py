"""MCP Server — 数学工具（stdio 传输）

对应课程章节：模块三 / 4.3.1

依赖:
uv pip install fastmcp
"""

from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """加法运算"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """乘法运算"""
    return a * b


@mcp.resource("formula://basic")
async def get_formulas() -> str:
    """返回基础数学公式"""
    return "面积 = 长 × 宽\n体积 = 长 × 宽 × 高"


@mcp.prompt()
def explain_math(topic: str) -> str:
    """生成数学解释提示"""
    return f"请用简单的语言解释 {topic} 的概念，并举例说明。"


if __name__ == "__main__":
    mcp.run(transport="stdio")
