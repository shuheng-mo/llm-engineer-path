"""MCP 客户端 — 拉取 files_server 暴露的资源

对应课程章节：模块三 / 4.4.2 客户端获取资源

运行步骤（两个终端）：
    # 终端 1：启动 server（默认监听 http://127.0.0.1:8000/mcp）
    uv run python stage2-advanced/04-langgraph/03_module_tools/05_mcp/servers/files_server.py

    # 终端 2：跑本客户端
    uv run python stage2-advanced/04-langgraph/03_module_tools/05_mcp/clients/fetch_files.py
"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "files": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp",
            }
        }
    )

    # 1) 列出 server 暴露的所有静态资源（参数化模板不会列出来，需按 URI 拉）
    print("=== files 提供的静态资源 ===")
    blobs = await client.get_resources("files")
    for blob in blobs:
        print(f"- URI: {blob.metadata.get('uri')} | MIME: {blob.mimetype}")
        print(blob.as_string())

    # 2) 按具体 URI 拉取参数化资源 docs://{category}/{filename}
    print("\n=== 按 URI 拉取参数化资源 ===")
    blobs = await client.get_resources(
        "files",
        uris=[
            "config://app.json",  # 静态资源也能这样点名拉
            "docs://api/getting-started.md",  # 参数化资源
            "docs://tutorial/quickstart.md",
        ],
    )
    for blob in blobs:
        print(f"- URI: {blob.metadata.get('uri')} | MIME: {blob.mimetype}")
        print(blob.as_string())


if __name__ == "__main__":
    asyncio.run(main())
