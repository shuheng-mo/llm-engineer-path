"""Store 语义搜索 — 配置 Embedding

对应课程章节：模块四 / 3.3.1
"""

import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langgraph.store.memory import InMemoryStore

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 维度需要匹配模型的输出维度
store = InMemoryStore(index={"dims": 1536, "embed": embeddings})
