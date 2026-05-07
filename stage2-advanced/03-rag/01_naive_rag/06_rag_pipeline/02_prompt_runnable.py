"""RAG Pipeline 第二步：动态注入 context 的 ChatPromptTemplate

对应课程章节：一 / 7.2.2
"""
from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """你是一个专业的问答助手。请根据以下提供的上下文信息回答用户的问题。

要求：
1. 只使用上下文中的信息回答问题
2. 如果上下文中没有相关信息，请诚实地说"根据现有资料，我无法回答这个问题"
3. 回答要简洁准确，并在适当时候引用来源

上下文信息：
{context}""",
    ),
    ("human", "{question}"),
])
