"""FAISS 向量库 — Meta 开源的本地向量库（4 种用法合集）

对应课程章节：一 / 5.4 扩展（FAISS 替代 Chroma）

依赖:
    rag group 已经装了 faiss-cpu；
    FAISS 不像 Chroma 是嵌入式数据库，它就是一个内存索引 + 文件序列化，更轻量更快。

跟 Chroma 的关键区别:
    1. FAISS 没有 collection_name —— 一个 index 一个目录
    2. 持久化 API 不同：save_local() / load_local()，存的是 .faiss + .pkl 两个文件
    3. load_local 必须传 allow_dangerous_deserialization=True（pickle 反序列化是不安全的）
    4. metadata filter 语法不同：传 lambda 而不是 {"category": "x"} 形式
    5. similarity_search_with_score 直接返回 L2 距离（越小越相似），可用于阈值过滤
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = Path(__file__).resolve().parents[2] / "data" / "LangChain.pdf"
PERSIST_DIR = Path(__file__).parent / "faiss_db"

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)


# ============================================================
# Part 1: from_texts — 直接从字符串列表建索引（内存模式）
# ============================================================
print("=" * 60)
print("Part 1: FAISS.from_texts —— 字符串列表建索引")
print("=" * 60)

texts = [
    "LangChain 是一个用于开发 LLM 应用的框架",
    "RAG 是检索增强生成的缩写",
    "向量数据库用于存储和检索向量",
    "Embedding 将文本转换为向量表示",
    "FAISS 是 Meta 开源的高性能向量检索库",
]

vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)

results = vectorstore.similarity_search("什么是 LangChain？", k=2)
for doc in results:
    print(f"  - {doc.page_content}")


# ============================================================
# Part 2: from_documents — 从切分好的 Document 列表建索引
# ============================================================
print("\n" + "=" * 60)
print("Part 2: FAISS.from_documents —— PDF → 切分 → 建索引")
print("=" * 60)

loader = PyPDFLoader(str(PDF_PATH))
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
)
chunks = splitter.split_documents(documents)
print(f"  文档切分得到 {len(chunks)} 个 chunks")

vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
print(f"  FAISS 索引向量数：{vectorstore.index.ntotal}")

results = vectorstore.similarity_search("什么是 LangChain？", k=3)
for idx, doc in enumerate(results, 1):
    print(f"  {idx}. {doc.page_content[:80]}...")


# ============================================================
# Part 3: save_local / load_local —— 持久化
# ============================================================
print("\n" + "=" * 60)
print("Part 3: FAISS 持久化 —— save_local + load_local")
print("=" * 60)

# 写入磁盘（生成 index.faiss + index.pkl 两个文件）
if PERSIST_DIR.exists():
    shutil.rmtree(PERSIST_DIR)
vectorstore.save_local(str(PERSIST_DIR))
print(f"  已保存到：{PERSIST_DIR}")
for f in PERSIST_DIR.iterdir():
    print(f"    - {f.name} ({f.stat().st_size} bytes)")

# 重新加载（注意：必须传 allow_dangerous_deserialization=True）
loaded_store = FAISS.load_local(
    str(PERSIST_DIR),
    embeddings,
    allow_dangerous_deserialization=True,  # 因为内部用 pickle，FAISS 强制要求显式确认
)
print(f"  重新加载，向量数：{loaded_store.index.ntotal}")

results = loaded_store.similarity_search("RAG 的工作原理", k=2)
for idx, doc in enumerate(results, 1):
    print(f"  {idx}. {doc.page_content[:80]}...")


# ============================================================
# Part 4: 带 Metadata 的存储 + 过滤检索（FAISS 用 lambda 而不是 dict）
# ============================================================
print("\n" + "=" * 60)
print("Part 4: Metadata 过滤检索（FAISS lambda 风格）")
print("=" * 60)

documents = [
    Document(
        page_content="Python 是一种解释型编程语言，语法简洁",
        metadata={"category": "programming", "level": "beginner"},
    ),
    Document(
        page_content="Rust 是一门系统级编程语言，强调内存安全",
        metadata={"category": "programming", "level": "advanced"},
    ),
    Document(
        page_content="机器学习是人工智能的一个分支",
        metadata={"category": "ai", "level": "beginner"},
    ),
    Document(
        page_content="Transformer 是一种基于注意力机制的深度学习架构",
        metadata={"category": "ai", "level": "advanced"},
    ),
]

vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)


# === 4.1 不带过滤 ===
print("\n[A] 不带过滤")
for doc in vectorstore.similarity_search("入门", k=4):
    print(f"  - [{doc.metadata['category']}/{doc.metadata['level']}] {doc.page_content}")


# === 4.2 用 lambda 过滤（FAISS 风格） ===
print("\n[B] 只看 category=programming")
for doc in vectorstore.similarity_search(
    "入门",
    k=4,
    filter=lambda meta: meta.get("category") == "programming",
):
    print(f"  - [{doc.metadata['category']}/{doc.metadata['level']}] {doc.page_content}")


# === 4.3 复合条件过滤 ===
print("\n[C] category=ai 且 level=advanced")
for doc in vectorstore.similarity_search(
    "深度学习",
    k=4,
    filter=lambda meta: meta.get("category") == "ai" and meta.get("level") == "advanced",
):
    print(f"  - [{doc.metadata['category']}/{doc.metadata['level']}] {doc.page_content}")


# === 4.4 带分数检索（FAISS 特色） ===
print("\n[D] similarity_search_with_score —— 看 L2 距离")
for doc, score in vectorstore.similarity_search_with_score("AI 入门", k=3):
    # score 是 L2 距离，越小越相似
    print(f"  - 距离 {score:.4f}  [{doc.metadata['category']}] {doc.page_content[:40]}...")
