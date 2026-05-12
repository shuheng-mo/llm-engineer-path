"""多路召回（Multi-Route Retrieval） — 多个知识库各自检索 + RRF 融合

对应课程章节：二 / 3.6
"""

import os
from collections import defaultdict
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()


class MultiRouteRetriever:
    def __init__(self):
        self.retrievers = {}
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        )

    def add_route(self, name: str, documents: list, retriever_type: str = "vector"):
        if retriever_type == "vector":
            vectorstore = Chroma.from_documents(documents, self.embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        elif retriever_type == "bm25":
            retriever = BM25Retriever.from_documents(documents)
            retriever.k = 3
        elif retriever_type == "hybrid":
            bm25 = BM25Retriever.from_documents(documents)
            bm25.k = 3
            vectorstore = Chroma.from_documents(documents, self.embeddings)
            vector = vectorstore.as_retriever(search_kwargs={"k": 3})
            retriever = EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])
        else:
            raise ValueError(f"Unknown retriever_type: {retriever_type}")

        self.retrievers[name] = retriever
        print(f"✅ 添加路径: {name} ({retriever_type})")

    def retrieve(self, query: str, top_n: int = 5) -> list:
        all_results = []
        for name, retriever in self.retrievers.items():
            results = retriever.invoke(query)
            print(f" {name}: 召回 {len(results)} 条")
            all_results.append(results)
        return self._rrf_fusion(all_results, top_n)

    @staticmethod
    def _rrf_fusion(results_list: list, top_n: int, k: int = 60) -> list:
        rrf_scores = defaultdict(float)
        doc_map = {}
        for results in results_list:
            for rank, doc in enumerate(results, start=1):
                doc_id = doc.page_content[:100]
                rrf_scores[doc_id] += 1 / (k + rank)
                doc_map[doc_id] = doc
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in sorted_docs[:top_n]]


if __name__ == "__main__":
    product_docs = [
        Document(
            page_content="iPhone 15 采用 A16 芯片，电池容量 3349mAh，支持 20W 快充。正常使用续航约 10-12 小时。"
        ),
        Document(
            page_content="iPhone 15 Pro 采用 A17 Pro 芯片，电池容量 3274mAh，支持 USB-C 接口充电。"
        ),
    ]
    faq_docs = [
        Document(
            page_content="Q: 手机电池不耐用怎么办？A: 1. 检查后台应用；2. 降低屏幕亮度；3. 开启省电模式；4. 如电池健康度低于80%建议更换。"
        ),
        Document(
            page_content="Q: 如何查看电池健康度？A: 进入设置 → 电池 → 电池健康度，可查看最大容量百分比。"
        ),
    ]
    ticket_docs = [
        Document(
            page_content="工单记录：用户反馈 iPhone 15 电池掉电快，经检测电池健康度 78%，建议用户到店更换电池，问题解决。"
        ),
        Document(
            page_content="工单记录：用户反馈手机发热严重，排查发现是某 App 后台持续运行，关闭后恢复正常。"
        ),
    ]

    retriever = MultiRouteRetriever()
    retriever.add_route("product_docs", product_docs, "vector")
    retriever.add_route("faq", faq_docs, "bm25")
    retriever.add_route("tickets", ticket_docs, "hybrid")

    query = "iPhone 15 电池不耐用怎么办？"
    print(f"\n 查询: {query}\n")

    results = retriever.retrieve(query, top_n=4)

    print(f"\n 多路召回最终结果 (Top-{len(results)}):")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content[:80]}...")
