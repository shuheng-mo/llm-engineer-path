"""带 Metadata 的存储与过滤

对应课程章节：一 / 5.3.3
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

load_dotenv()

documents = [
    Document(
        page_content="Python 是一种编程语言",
        metadata={"source": "python.pdf", "page": 1, "category": "programming"},
    ),
    Document(
        page_content="机器学习基础概念",
        metadata={"source": "ml.pdf", "page": 1, "category": "ai"},
    ),
]

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

# 带过滤条件的搜索
results = vectorstore.similarity_search(
    query="基础",
    k=5,
    filter={"category": "programming"},  # 只搜索编程类文档1
)

for idx, doc in enumerate(results, 1):
    print(idx, "->>>>>>>", doc.page_content)
