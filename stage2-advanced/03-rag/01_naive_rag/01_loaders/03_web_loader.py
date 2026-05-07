"""WebBaseLoader — 加载网页

对应课程章节：一 / 2.2.3
"""
from langchain_community.document_loaders import WebBaseLoader

# 加载单个网页
loader = WebBaseLoader("https://reference.langchain.org.cn/python/langchain_core")
docs = loader.load()
print(docs)

# 加载多个网页
loader = WebBaseLoader([
    "https://example.com/page1",
    "https://example.com/page2",
])
docs = loader.load()
print(f"共加载 {len(docs)} 个网页")
