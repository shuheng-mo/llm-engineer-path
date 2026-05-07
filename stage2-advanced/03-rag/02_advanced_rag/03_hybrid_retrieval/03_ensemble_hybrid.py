"""EnsembleRetriever — 把 BM25 和向量检索按权重融合

对应课程章节：二 / 3.4 第一步~第二步

依赖:
uv pip install langchain-classic
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
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

# 关键词检索
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 4

# 向量检索
vectorstore = Chroma.from_documents(chunks, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 混合：weights 加起来 = 1
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6],   # BM25 40%，向量 60%
)

results = ensemble_retriever.invoke("RecursiveCharacterTextSplitter 怎么用？")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content[:80]}...")
