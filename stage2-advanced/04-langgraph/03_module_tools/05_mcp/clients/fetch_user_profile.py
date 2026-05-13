"""MCP 客户端 — 调用 data_server 的结构化输出工具

对应课程章节：模块三 / 4.4.1 工具结构化内容

data_server 的 get_user_profile 工具返回一个 dict，包含人类可读的 text
和机器可解析的 structured_content。客户端拿到 ToolMessage 后两部分都能用。

运行步骤（两个终端）：
    # 终端 1：启动 server（默认监听 http://127.0.0.1:8000/mcp）
    uv run python stage2-advanced/04-langgraph/03_module_tools/05_mcp/servers/data_server.py

    # 终端 2：跑本客户端
    uv run python stage2-advanced/04-langgraph/03_module_tools/05_mcp/clients/fetch_user_profile.py
"""

import asyncio
import json

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "data": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp",
            }
        }
    )

    # 1) 列出 server 暴露的工具
    tools = await client.get_tools()
    print("=== data 提供的工具 ===")
    for t in tools:
        print(f"- {t.name}: {t.description}")
        print(f"  args_schema: {t.args_schema}")

    # 2) 直接调用工具（绕过 LLM）—— 学习阶段最直观的方式
    get_user_profile = next(t for t in tools if t.name == "get_user_profile")

    raw = await get_user_profile.ainvoke({"user_id": "u_001"})
    print("\n=== 工具原始返回（已被 langchain-mcp-adapters 序列化为字符串）===")
    print(raw)

    # 3) 解析出 structured_content —— server 端是 dict，序列化成 JSON 字符串了
    payload = json.loads(raw)
    print("\n=== 拆开看两部分 ===")
    print(f"text             : {payload['text']}")
    print(f"structured_content: {payload['structured_content']}")
    profile = payload["structured_content"]
    print(f"  → 姓名: {profile['name']}, 年龄: {profile['age']}, 邮箱: {profile['email']}")


if __name__ == "__main__":
    asyncio.run(main())
