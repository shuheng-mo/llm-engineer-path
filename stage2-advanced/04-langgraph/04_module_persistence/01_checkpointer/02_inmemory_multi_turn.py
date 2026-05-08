"""Checkpointer 多轮对话 — thread_id 隔离不同会话

对应课程章节：模块四 / 2.2.2
"""
from langchain_core.messages import HumanMessage

# from .01_inmemory_basic import graph
graph = None  # 占位 — 在实际项目中 import 上一步的 graph

thread_config = {"configurable": {"thread_id": "session_user_123"}}

result1 = graph.invoke({"messages": [HumanMessage(content="你好，我叫张三")]}, config=thread_config)
print(result1["messages"][-1].content)

# 第二次：同一个 thread_id —— 自动加载历史
result2 = graph.invoke({"messages": [HumanMessage(content="我刚才说我叫什么？")]}, config=thread_config)
print(result2["messages"][-1].content)

# 不同 thread_id —— 全新会话，无法记住
result3 = graph.invoke(
    {"messages": [HumanMessage(content="我刚才说了什么？")]},
    config={"configurable": {"thread_id": "session_user_456"}},
)
print(result3["messages"][-1].content)
