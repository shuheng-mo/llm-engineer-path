"""调试 Runnable Chain — astream_events v2 查看每一步的执行过程

对应课程章节：一 / 7.5
"""
import asyncio

# 假设外部已经构建好 rag_chain（参考 06_full_pipeline.py）
# from .full_pipeline import rag_chain


async def debug_rag_chain():
    question = "什么是向量数据库？"

    async for event in rag_chain.astream_events(question, version="v2"):  # noqa: F821
        kind = event["event"]
        name = event["name"]

        if kind == "on_retriever_end":
            print(f"\n📚 检索完成，获取到 {len(event['data']['output'])} 个文档")
        elif kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)
        elif kind == "on_chain_end":
            print(f"\n✅ {name} 执行完成")


if __name__ == "__main__":
    asyncio.run(debug_rag_chain())
