"""MCP Server — Prompt 模板

对应课程章节：模块三 / 4.4.3
"""

from fastmcp import FastMCP

mcp = FastMCP("Prompts")


@mcp.prompt()
def code_review(language: str, focus: str = "general") -> str:
    """生成代码审查提示"""
    return f"""请审查以下 {language} 代码，重点关注{focus}方面：
    1. 代码质量
    2. 潜在bug
    3. 最佳实践
    """


@mcp.prompt()
def summarize(style: str = "concise") -> list:
    """生成摘要提示（返回消息列表）"""
    return [
        {"role": "system", "content": f"你是一个{style}的摘要助手"},
        {"role": "user", "content": "请总结以下内容"},
    ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
