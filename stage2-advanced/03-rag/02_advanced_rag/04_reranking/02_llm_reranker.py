"""LLM Reranker — 当精度要求极高时，让大模型给文档打分

对应课程章节：二 / 4.4
"""
import os
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMReranker:
    def __init__(self, top_n: int = 5):
        self.top_n = top_n
        self.llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0,
        )

        self.score_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """评估文档与查询的相关性，给出 0-10 的分数。
只输出一个数字，不要有任何其他内容。

评分标准：
- 0-3：不相关
- 4-6：部分相关
- 7-10：高度相关""",
            ),
            ("human", "查询：{query}\n\n文档：{document}\n\n相关性分数："),
        ])

    def _score_document(self, query: str, document: str) -> float:
        response = (self.score_prompt | self.llm).invoke({"query": query, "document": document})
        try:
            return float(response.content.strip())
        except Exception:
            return 0.0

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        scored_docs = []
        for doc in documents:
            score = self._score_document(query, doc.page_content)
            scored_docs.append((doc, score))
            print(f"   评分 {score:.1f}: {doc.page_content[:40]}...")

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[: self.top_n]]


if __name__ == "__main__":
    reranker = LLMReranker(top_n=3)
    query = "什么是 RAG？"
    initial_results = [
        Document(page_content="RAG 是检索增强生成的缩写，它结合了检索和生成两种能力。"),
        Document(page_content="Python 是一种流行的编程语言。"),
        Document(page_content="RAG 可以有效解决 LLM 的幻觉问题和知识时效性问题。"),
        Document(page_content="机器学习是人工智能的一个分支。"),
    ]
    reranked = reranker.rerank(query, initial_results)
    print(" 检索结果:")
    for i, doc in enumerate(reranked, 1):
        print(f"   {i}. {doc.page_content[:50]}...")
