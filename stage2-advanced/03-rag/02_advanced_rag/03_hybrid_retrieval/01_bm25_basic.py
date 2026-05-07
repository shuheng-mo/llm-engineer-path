"""BM25 入门 — 关键词匹配的稀疏检索

对应课程章节：二 / 3.2

依赖:
uv pip install rank_bm25
"""
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

docs = [
    Document(page_content="RecursiveCharacterTextSplitter 是 LangChain 中最常用的文本分割器，它会递归地尝试不同的分隔符来分割文本。"),
    Document(page_content="文本分割是 RAG 流程中的关键步骤，好的分割策略可以显著提升检索效果。"),
    Document(page_content="LangChain 提供了多种分割器，包括按字符、按句子、按段落等方式。"),
    Document(page_content="使用 RecursiveCharacterTextSplitter 时，需要设置 chunk_size 和 chunk_overlap 参数。"),
    Document(page_content="向量检索通过语义相似度来匹配文档，而 BM25 通过关键词匹配。"),
]

bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3

query = "RecursiveCharacterTextSplitter 怎么用？"
results = bm25_retriever.invoke(query)

print(f"查询: {query}\n")
print("BM25 检索结果:")
for i, doc in enumerate(results):
    has_keyword = "RecursiveCharacterTextSplitter" in doc.page_content
    mark = "YES" if has_keyword else "NO"
    print(f"   {i + 1}. {mark} {doc.page_content[:50]}...")
