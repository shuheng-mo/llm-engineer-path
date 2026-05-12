"""ToolNode 并行执行 — 一次 AIMessage 携带多个 tool_calls 时并发执行

对应课程章节：模块三 / 2.2.3
"""

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

# 复用 02_toolnode_basic.py 中定义的 tools
# from .02_toolnode_basic import tools

tools = []  # 占位 — 引用上一个文件的 tools

ai_message = AIMessage(
    content="",
    tool_calls=[
        {"name": "get_weather", "args": {"city": "北京"}, "id": "call_1"},
        {"name": "get_weather", "args": {"city": "上海"}, "id": "call_2"},
        {"name": "get_time", "args": {}, "id": "call_3"},
    ],
)

workflow = StateGraph(MessagesState)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "tools")
workflow.add_edge("tools", END)

app = workflow.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [ai_message]})
    for msg in result["messages"]:
        print(f"[{msg.type}]: {msg.content}")
