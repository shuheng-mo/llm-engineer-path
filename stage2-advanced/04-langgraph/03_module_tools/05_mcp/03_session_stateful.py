"""MCP 客户端 — 持久 Session（多次调用共享状态）

对应课程章节：模块三 / 4.3.5
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools


async def main():
    client = MultiServerMCPClient({})

    async with client.session("math") as session:
        tools = await load_mcp_tools(session)
        agent = create_agent("claude-sonnet-4-5-20250929", tools)

        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": "设置变量 x=10，然后计算 x+5"}],
        })
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
