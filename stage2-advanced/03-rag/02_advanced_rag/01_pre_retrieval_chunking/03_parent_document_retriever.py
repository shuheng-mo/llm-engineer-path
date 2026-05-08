"""ParentDocumentRetriever — 子块检索 + 父块返回（更完整的上下文）

对应课程章节：二 / 1.5

依赖:
uv pip install langchain-classic
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.stores import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 父块用于返回（提供完整上下文），子块用于检索（提高匹配精度）
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)

vectorstore = Chroma(collection_name="child_chunks", embedding_function=embeddings)
docstore = InMemoryStore()  # 存父块原文

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

loader = PyPDFLoader(str(DATA_DIR / "LangChain.pdf"))
documents = loader.load()
retriever.add_documents(documents)

# 检索返回的是父文档
results = retriever.invoke("什么是 RAG？")
for i, doc in enumerate(results, 1):
    print(f"结果 {i}（长度 {len(doc.page_content)} 字符）:")
    print(doc.page_content[:200] + "...")
