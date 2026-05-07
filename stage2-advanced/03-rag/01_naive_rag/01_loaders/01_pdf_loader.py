"""PyPDFLoader — 加载 PDF 文档

对应课程章节：一 / 2.2 常用文档加载器

依赖:
uv pip install pypdf
"""
from langchain_community.document_loaders import PyPDFLoader

# 加载单个 PDF 文件
loader = PyPDFLoader("documents/report.pdf")
pages = loader.load()

# 查看加载结果
for page in pages:
    print(f"页码: {page.metadata['page']}")
    print(f"内容预览: {page.page_content[:200]}...")
    print("-" * 50)
