"""长期记忆 — Embedding + Chroma 存储用户记忆

对应课程章节：第七章 / 4.2

依赖:
uv pip install -U langchain-chroma
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

vectorstore = Chroma(
    collection_name="user_memory",
    embedding_function=embeddings,
    persist_directory="./memory_db",
)


def save_memory(user_id: str, content: str, memory_type: str = "general"):
    """保存一条长期记忆"""
    doc = Document(
        page_content=content,
        metadata={
            "user_id": user_id,
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat(),
        },
    )
    vectorstore.add_documents([doc])


# 示例：保存用户信息
save_memory("user_001", "用户名字是小明", "profile")
save_memory("user_001", "用户是一名Python后端开发工程师", "profile")
save_memory("user_001", "用户喜欢简洁的代码风格", "preference")
save_memory("user_001", "用户正在开发一个电商推荐系统", "project")


def retrieve_memories(user_id: str, query: str, k: int = 3) -> list[str]:
    """检索与查询相关的记忆"""
    results = vectorstore.similarity_search(query, k=k, filter={"user_id": user_id})
    return [doc.page_content for doc in results]


memories = retrieve_memories("user_001", "用户的职业是什么？")
print(memories)


# 查看 user_001 的所有记忆
all_docs = vectorstore._collection.get(
    where={"user_id": "user_001"},
    include=["documents", "metadatas"],
)
print("总数：", len(all_docs["ids"]))
for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]):
    print(doc, meta)
