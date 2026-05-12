"""策略 2：删除消息（Remove Messages）— 物理删除旧消息

对应课程章节：模块四 / 4.3
"""

from langchain_core.messages import RemoveMessage
from langgraph.graph import END, START, MessagesState, StateGraph


def manage_memory(state: MessagesState):
    messages = state["messages"]
    if len(messages) > 4:
        num_to_remove = len(messages) - 4
        messages_to_remove = messages[:num_to_remove]
        print(f"Debug: 正在物理删除 {len(messages_to_remove)} 条旧消息...")
        return {"messages": [RemoveMessage(id=m.id) for m in messages_to_remove]}
    return {}


def simple_bot(state: MessagesState):
    last_msg = state["messages"][-1]
    return {"messages": [("ai", f"收到：{last_msg.content}")]}


builder = StateGraph(MessagesState)
builder.add_node("bot", simple_bot)
builder.add_node("cleaner", manage_memory)

builder.add_edge(START, "bot")
builder.add_edge("bot", "cleaner")
builder.add_edge("cleaner", END)

app = builder.compile()
