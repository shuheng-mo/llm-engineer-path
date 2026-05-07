"""Markdown 文档加载（Unstructured + TextLoader 两种方式）

对应课程章节：一 / 2.2.2

依赖:
uv pip install unstructured markdown
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader, TextLoader

# 方式 1：UnstructuredMarkdownLoader（保留 Markdown 结构信息）
loader = UnstructuredMarkdownLoader("docs/README.md")
documents = loader.load()
print("UnstructuredMarkdownLoader 结果数量:", len(documents))

# 方式 2：TextLoader（极简版，只读取纯文本）
loader = TextLoader("docs/LangChain.md", encoding="utf-8")
documents = loader.load()
print("文档内容：\n", documents[0].page_content)
