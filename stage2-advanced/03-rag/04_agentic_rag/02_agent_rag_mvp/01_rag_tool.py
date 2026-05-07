"""Agent + RAG MVP — 把检索器封装成 @tool

对应课程章节：四 / 第二章 2.5.2

依赖:
uv pip install -U langchain langchain-community langgraph dashscope python-dotenv chromadb
"""
import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool

load_dotenv()
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

# 1. 模拟数据
texts = [
    "Agentic RAG 是一种结合了代理自主性与检索增强生成的技术。",
    "LangGraph 是 LangChain 推出的用于构建有环图应用的编排框架。",
    "Qwen-3.0 是阿里云通义千问团队在2025年发布的强大开源模型。",
]

# 2. 向量化 + Chroma
embeddings = DashScopeEmbeddings(model="text-embedding-v1")
vectorstore = Chroma.from_texts(texts, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})


# 3. 把检索器封成 @tool（Agentic RAG 的核心）
@tool
def lookup_knowledge_base(query: str) -> str:
    """当需要查询关于 Agentic RAG、LangGraph 或 Qwen 模型的技术细节时，
    必须使用此工具。输入应该是具体、明确的查询字符串。"""
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join(d.page_content for d in docs)


tools = [lookup_knowledge_base]
