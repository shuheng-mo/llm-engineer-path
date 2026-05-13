"""MCP 客户端进阶 — 加载 Resources 和 Prompts

对应课程章节：模块三 / 4.2.3 进阶
"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient({})  # 这里只是保存配置，不会真的连接

    # 1. 工具
    tools = await client.get_tools()
    print("\n=== TOOLS ===")
    for t in tools:
        print(f"- {t.name}: {t.description}")
        print(f"  args_schema: {t.args_schema}")

    # 2. 资源（文件、数据等）
    print("\n=== RESOURCES (math) ===")
    math_blobs = await client.get_resources("math")
    print(f"resources count: {len(math_blobs)}")
    for blob in math_blobs:
        print(f"- URI: {blob.metadata.get('uri')} | MIME: {blob.mimetype}")
        print(blob.as_string())

    print("\n=== RESOURCES (weather, by URI) ===")
    blobs = await client.get_resources("weather", uris=["weather://北京/history"])
    for blob in blobs:
        print(f"- URI: {blob.metadata.get('uri')} | MIME: {blob.mimetype}")
        print(blob.as_string())

    # 3. 提示模板
    messages = await client.get_prompt(
        server_name="math",
        prompt_name="explain_math",
        arguments={"topic": "计算 3 × 12"},
    )
    print(messages)


if __name__ == "__main__":
    asyncio.run(main())
