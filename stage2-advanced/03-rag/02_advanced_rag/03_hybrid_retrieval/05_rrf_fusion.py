"""RRF（Reciprocal Rank Fusion）融合算法 — 多检索结果按排名互相抵消的优雅写法

对应课程章节：二 / 3.5
"""
import os
from collections import defaultdict
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

documents = [
    Document(page_content="RecursiveCharacterTextSplitter 是 LangChain 中最常用的文本分割器，它会递归地尝试不同的分隔符来分割文本。"),
    Document(page_content="文本分割是 RAG 流程中的关键步骤，好的分割策略可以显著提升检索效果。"),
    Document(page_content="LangChain 提供了多种分割器，包括按字符、按句子、按段落等方式。"),
    Document(page_content="使用 RecursiveCharacterTextSplitter 时，需要设置 chunk_size 和 chunk_overlap 参数。"),
    Document(page_content="向量检索通过语义相似度来匹配文档，而 BM25 通过关键词匹配。"),
]

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = splitter.split_documents(documents)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 4

vectorstore = Chroma.from_documents(chunks, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


def reciprocal_rank_fusion(results_list: list, k: int = 60, top_n: int = 10) -> list:
    """RRF 融合多个检索结果。

    score = sum(1 / (k + rank))，rank 从 1 开始，k 通常取 60。
    """
    rrf_scores = defaultdict(float)
    doc_map = {}

    for results in results_list:
        for rank, doc in enumerate(results, start=1):
            doc_id = doc.page_content[:100]    # 用前 100 字作为去重 key
            rrf_scores[doc_id] += 1 / (k + rank)
            doc_map[doc_id] = doc

    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_map[doc_id] for doc_id, _ in sorted_docs[:top_n]]


if __name__ == "__main__":
    query = "RecursiveCharacterTextSplitter 怎么用？"
    bm25_results = bm25_retriever.invoke(query)
    vector_results = vector_retriever.invoke(query)

    rrf_results = reciprocal_rank_fusion([bm25_results, vector_results], k=60, top_n=5)
    print("📌 RRF 融合结果:")
    for i, doc in enumerate(rrf_results, 1):
        print(f"   {i}. {doc.page_content[:60]}...")
