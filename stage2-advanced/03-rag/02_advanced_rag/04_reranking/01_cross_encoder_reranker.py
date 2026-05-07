"""Cross-Encoder 重排序 — 使用 BAAI/bge-reranker-v2-m3 模型

对应课程章节：二 / 4.3

依赖:
uv pip install -U sentence-transformers
"""
from typing import List

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


class BGEReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", top_n: int = 5):
        self.model = CrossEncoder(model_name)
        self.top_n = top_n
        print(f" 加载重排序模型: {model_name}")

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        if not documents:
            return []

        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[: self.top_n]]


if __name__ == "__main__":
    reranker = BGEReranker(top_n=3)

    query = "什么是 RAG？"
    initial_results = [
        Document(page_content="RAG 是检索增强生成的缩写，它结合了检索和生成两种能力。"),
        Document(page_content="Python 是一种流行的编程语言。"),
        Document(page_content="检索增强生成（RAG）是一种将外部知识与 LLM 结合的技术。"),
        Document(page_content="机器学习是人工智能的一个分支。"),
        Document(page_content="RAG 可以有效解决 LLM 的幻觉问题和知识时效性问题。"),
    ]

    reranked = reranker.rerank(query, initial_results)

    print(f" 查询: {query}")
    print("\n重排序前 Top-3:")
    for i, doc in enumerate(initial_results[:3], 1):
        print(f"   {i}. {doc.page_content[:50]}...")

    print("\n重排序后 Top-3:")
    for i, doc in enumerate(reranked, 1):
        print(f"   {i}. {doc.page_content[:50]}...")
