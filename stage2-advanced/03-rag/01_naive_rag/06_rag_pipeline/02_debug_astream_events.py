"""调试 RAG Chain — astream_events v2 看每一步的执行过程

对应课程章节：一 / 7.5

为什么需要这个？
    chain.invoke() 是一次性返回最终答案，中间过程是黑盒。
    chain.stream() 只能流式拿到 LLM 的输出 chunk，看不到 retriever / prompt 的执行。
    chain.astream_events("...", version="v2") 是 LCEL 的杀手级特性：
    把链内**每个 Runnable** 的 start / stream / end 事件都吐出来，定位问题神器。

主要事件类型：
    on_retriever_start / on_retriever_end       检索器执行前后
    on_prompt_start    / on_prompt_end          prompt 模板渲染前后
    on_chat_model_start / on_chat_model_stream / on_chat_model_end
                                                LLM 调用 + 流式输出 chunk
    on_parser_start    / on_parser_end          OutputParser 前后
    on_chain_start     / on_chain_end           整条链 / 子链的边界
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
load_dotenv()


# ============================================================
# 复用 01_full_pipeline.py 已经持久化好的向量库
# ============================================================
# 假设你已经跑过一次 01_full_pipeline.py —— Chroma 数据已经在 data/chroma_db/，
# 这里直接打开，避免重复 embed（节约时间和 API 费用）。
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)
vectorstore = Chroma(
    persist_directory=str(DATA_DIR / "chroma_db"),
    embedding_function=embeddings,
)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 10})

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[文档片段 {i + 1}]\n{doc.page_content}" for i, doc in enumerate(docs)
    )


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是文档问答助手。\n\n参考资料：\n{context}\n\n请根据资料回答问题。"),
        ("human", "{question}"),
    ]
)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)


# ============================================================
# astream_events 调试
# ============================================================
async def debug_rag_chain():
    question = "什么是向量数据库？"

    async for event in rag_chain.astream_events(question, version="v2"):
        kind = event["event"]
        name = event["name"]

        # 检索完成 —— 看到拿到了几个文档
        if kind == "on_retriever_end":
            docs = event["data"]["output"]
            print(f"\n📚 检索完成，获取到 {len(docs)} 个文档")
            for i, doc in enumerate(docs, 1):
                print(f"  {i}. {doc.page_content[:60]}...")

        # LLM 流式输出 —— 边生成边打印
        elif kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)

        # 子链 / 整链结束（用 name 区分是谁结束）
        elif kind == "on_chain_end":
            print(f"\n✅ {name} 执行完成")


if __name__ == "__main__":
    asyncio.run(debug_rag_chain())
