"""Chroma.from_texts — 直接从字符串列表创建向量库（内存模式）

对应课程章节：一 / 5.3.1（from_texts 用法）
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

texts = [
    "LangChain 是一个用于开发 LLM 应用的框架",
    "RAG 是检索增强生成的缩写",
    "向量数据库用于存储和检索向量",
    "Embedding 将文本转换为向量表示",
]

# 创建向量数据库（内存模式）
vectorstore = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    collection_name="my_collection",
    # persist_directory="./chroma_db",  # 取消注释即可写入磁盘
)

# 相似度搜索
results = vectorstore.similarity_search(query="什么是 LangChain？", k=2)
for doc in results:
    print(doc.page_content)
