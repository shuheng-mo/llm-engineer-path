"""消息角色 — system / human / ai 多轮对话

对应课程章节：第四章 / 2.3
"""
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的编程助手，专注于 Python 开发。"),
    ("human", "请帮我写一个排序函数"),
    ("ai", "好的，这是一个快速排序的实现：..."),
    ("human", "{followup_question}"),
])

messages = template.format_messages(followup_question="能解释一下这个算法的时间复杂度吗？")
for msg in messages:
    print(f"[{msg.type}] {msg.content}")
