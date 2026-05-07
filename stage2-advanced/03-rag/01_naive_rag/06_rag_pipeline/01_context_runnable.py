"""RAG Pipeline 第一步：检索 + 文档格式化（作为 Runnable 子节点）

对应课程章节：一 / 7.2.1
"""
from langchain_core.runnables import RunnablePassthrough  # noqa: F401  # 演示中会用到

# 假设外部已经准备好了 vectorstore
# from langchain_chroma import Chroma
# vectorstore = Chroma(...)

# 把检索器作为 Runnable
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


def format_docs(docs):
    """将检索到的文档格式化为字符串。"""
    return "\n\n".join(
        f"[来源: {doc.metadata.get('source', '未知')}]\n{doc.page_content}"
        for doc in docs
    )
