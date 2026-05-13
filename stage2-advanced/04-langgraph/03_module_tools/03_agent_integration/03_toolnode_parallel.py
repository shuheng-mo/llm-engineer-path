"""ToolNode 并行执行 — 一次 AIMessage 携带多个 tool_calls 时并发执行

对应课程章节：模块三 / 2.2.3
"""

from datetime import datetime

from langchain.tools import tool
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


# 与 02_toolnode_basic.py 中的 tools 保持一致（文件名以数字开头无法直接 import，故在此重新定义）
@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天，25°C"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [get_weather, get_time]

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
