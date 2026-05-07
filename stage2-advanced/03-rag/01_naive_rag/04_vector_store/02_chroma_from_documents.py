"""Chroma.from_documents — 用 PDF 切分后的 Document 列表持久化向量库

对应课程章节：一 / 5.3.1（from_documents 用法）
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 1. 加载文档
loader = PyPDFLoader("docs/LangChain.pdf")
documents = loader.load()

# 2. 切分
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
)
chunks = splitter.split_documents(documents)

# 3. Embedding
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 4. 创建持久化向量数据库
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="knowledge_base",
)

# 5. 相似度搜索
results = vectorstore.similarity_search(query="什么是 LangChain？", k=2)
for idx, doc in enumerate(results, 1):
    print(idx, "->>>>>>>", doc.page_content)
