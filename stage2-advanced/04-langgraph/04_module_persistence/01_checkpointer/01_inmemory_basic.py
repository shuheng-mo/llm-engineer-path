"""InMemorySaver 基础用法 — 编译时传 checkpointer

对应课程章节：模块四 / 2.2.1
"""

import pathlib
import sys

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, START, StateGraph

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

checkpointer = MemorySaver()

model = get_chat_model("qwen-max", temperature=0.3)


def chatbot(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chatbot)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile(checkpointer=checkpointer)
