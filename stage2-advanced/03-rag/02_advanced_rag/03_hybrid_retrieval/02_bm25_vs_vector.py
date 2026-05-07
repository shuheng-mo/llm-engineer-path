"""对比 BM25（关键词） vs 向量检索（语义） — GIL 案例

对应课程章节：二 / 3.2 动手实验
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()

docs = [
    Document(page_content=(
        "【定义】GIL（Global Interpreter Lock，全局解释器锁）是 CPython 的机制："
        "同一时刻只允许一个线程执行 Python 字节码。关键词：GIL 全局解释器锁 CPython 多线程 字节码"
    )),
    Document(page_content=(
        "【影响】在 CPython 中，GIL 会限制 Python 多线程并行执行 CPU 密集型任务，"
        "导致多线程性能受限。关键词：GIL 多线程 并行 CPU密集 CPython"
    )),
    Document(page_content=(
        "【绕过】想要真正并行（parallel）执行 CPU 密集计算，可使用多进程 multiprocessing 来绕过 GIL。"
        "关键词：绕过GIL 多进程 multiprocessing 并行 进程"
    )),
    Document(page_content=(
        "【补充】GIL 是 CPython 的实现细节；Jython、IronPython 等实现通常没有 GIL（或机制不同）。"
    )),
]

bm25 = BM25Retriever.from_documents(docs)
bm25.k = 2

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)
vectorstore = Chroma.from_documents(docs, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

query = "什么是 GIL？"
print(f"查询: {query}\n")

print("BM25 结果（关键词匹配）:")
for i, doc in enumerate(bm25.invoke(query)):
    has_gil = "GIL" in doc.page_content
    print(f"   {i + 1}. {'YES' if has_gil else 'NO'} {doc.page_content[:40]}...")

print("\n向量检索结果（语义相似）:")
for i, doc in enumerate(vector_retriever.invoke(query)):
    has_gil = "GIL" in doc.page_content
    print(f"   {i + 1}. {'YES' if has_gil else 'NO'} {doc.page_content[:40]}...")
