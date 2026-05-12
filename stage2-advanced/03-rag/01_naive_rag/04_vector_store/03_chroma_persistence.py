"""加载已有的 Chroma 持久化目录

对应课程章节：一 / 5.3.2
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 直接打开已有数据库（不会重新写入）
vectorstore = Chroma(
    persist_directory=str(DATA_DIR / "chroma_db"),
    embedding_function=embeddings,
    collection_name="knowledge_base",
)

print("已有 collection 数据：", vectorstore._collection.count())
