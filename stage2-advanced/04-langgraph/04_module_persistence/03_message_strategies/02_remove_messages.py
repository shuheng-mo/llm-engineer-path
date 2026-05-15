"""策略 2：删除消息（Remove Messages）— 物理删除旧消息

对应课程章节：模块四 / 4.3
"""

from langchain_core.messages import HumanMessage
from langchain_core.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
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

app = builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    config: RunnableConfig = {"configurable": {"thread_id": "qwen_clear_test"}}
    questions = [
        "我叫 Alice，今年 28 岁，住在上海。",
        "我有一只叫 Luna 的猫，今年三岁。",
        "Luna 最喜欢吃金枪鱼罐头，最讨厌洗澡。",
        "我的猫叫什么名字？我叫什么？",
        "清除我俩的对话历史！",
    ]

    for q in questions:
        res = app.invoke({"messages": [HumanMessage(content=q)]}, config)
        print(f"Qwen: {res['messages'][-1].content}")
