"""Checkpointer 多轮对话 — thread_id 隔离不同会话

对应课程章节：模块四 / 2.2.2
"""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, START, StateGraph
import pathlib
import sys

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-turbo", temperature=0.7, top_p=0.9)

checkpointer = MemorySaver()


def chatbot(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chatbot)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=checkpointer)  # 占位 — 在实际项目中 import 上一步的 graph

thread_config = {"configurable": {"thread_id": "session_user_123"}}

result1 = graph.invoke({"messages": [HumanMessage(content="你好，我叫张三")]}, config=thread_config)
print(result1["messages"][-1].content)

# 第二次：同一个 thread_id —— 自动加载历史
result2 = graph.invoke(
    {"messages": [HumanMessage(content="我刚才说我叫什么？")]}, config=thread_config
)
print(result2["messages"][-1].content)

# 不同 thread_id —— 全新会话，无法记住
result3 = graph.invoke(
    {"messages": [HumanMessage(content="我刚才说了什么？")]},
    config={"configurable": {"thread_id": "session_user_456"}},
)
print(result3["messages"][-1].content)
