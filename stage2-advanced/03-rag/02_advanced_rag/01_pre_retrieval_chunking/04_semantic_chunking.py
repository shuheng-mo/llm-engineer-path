"""SemanticChunker — 用 Embedding 相似度判断切分点（语义分块）

对应课程章节：二 / 1.6

依赖:
uv pip install langchain-experimental
"""
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90,
    buffer_size=1,
)

loader = PyPDFLoader("docs/LangChain.pdf")
documents = loader.load()
full_text = "\n".join(doc.page_content for doc in documents)

chunks = semantic_splitter.split_text(full_text)

print(f"语义分块结果：共 {len(chunks)} 个块")
print(f"平均块长度：{sum(len(c) for c in chunks) / len(chunks):.0f} 字符\n")

for i, chunk in enumerate(chunks[:3]):
    print(f"--- 块 {i + 1} ({len(chunk)} 字符) ---")
    print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    print()
