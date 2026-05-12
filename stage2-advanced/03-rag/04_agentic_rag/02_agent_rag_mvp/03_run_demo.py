"""Agent + RAG MVP — 运行演示（stream_mode=values 看中间过程）

对应课程章节：四 / 第二章 2.5.4
"""

from langchain_core.messages import HumanMessage

# from .02_langgraph_app import app

inputs = {"messages": [HumanMessage(content="LangGraph 是用来做什么的？")]}

for event in app.stream(inputs, stream_mode="values"):  # noqa: F821
    message = event["messages"][-1]
    print(f"[{message.type}]: {message.content}")
    if hasattr(message, "tool_calls") and message.tool_calls:
        print(f"   >>> 触发工具: {message.tool_calls[0]['name']}")

# 预期流程：human -> ai (tool_call) -> tool -> ai (合成回答)
