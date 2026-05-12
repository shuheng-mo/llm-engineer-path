"""图状态定义 — GraphState

对应课程章节：四 / 第四章 4.1
"""

from typing import List

from langchain_core.documents import Document
from typing_extensions import TypedDict


class GraphState(TypedDict):
    question: str  # 用户原始问题
    generation: str  # LLM 生成的答案
    documents: List[Document]  # 检索到的文档列表
    search_count: int  # 计数器，防止死循环
