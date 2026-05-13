"""MCP 客户端 — MultiServerMCPClient 同时连 stdio 和 http server

对应课程章节：模块三 / 4.2.3 基础用法

依赖:
uv pip install langchain-mcp-adapters
"""

import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# 假设已经初始化好 model
# from .. import model


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["./servers/math_server.py"],
            },
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        }
    )

    tools = await client.get_tools()
    agent = create_agent(model, tools)  # noqa: F821

    result1 = await agent.ainvoke({"messages": [{"role": "user", "content": "计算 3 × 12"}]})
    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": "纽约天气如何？"}]})

    print(result1)
    print(result2)


if __name__ == "__main__":
    asyncio.run(main())
