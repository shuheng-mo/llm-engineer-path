"""ToolNode 并行执行 — 一次 AIMessage 携带多个 tool_calls 时并发执行

对应课程章节：模块三 / 2.2.3
"""

import pathlib
import sys

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_time, get_weather  # noqa: E402

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
