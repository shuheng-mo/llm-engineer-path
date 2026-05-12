"""vectorstore.as_retriever() — v1.x 推荐的检索器接口

对应课程章节：一 / 6.2
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

vectorstore = Chroma(persist_directory=str(DATA_DIR / "chroma_db"), embedding_function=embeddings)

# 默认检索器
retriever = vectorstore.as_retriever()

# 带参数的检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",  # similarity | mmr | similarity_score_threshold
    search_kwargs={"k": 4},
)

docs = retriever.invoke("什么是 RAG？")
for doc in docs:
    print(doc.page_content[:100])

# 注意这里不会返回任何东西 你得先向量化RAG相关的文档到上方指定的文件目录
