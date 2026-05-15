"""策略 1：修剪消息（Trim Messages）— 保留最近 N 个 token

对应课程章节：模块四 / 4.2
"""

import pathlib
import sys

from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


def call_model_with_trimming(state: MessagesState):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=100,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )
    print(f"Debug: 实际发送给模型的消息数: {len(trimmed_messages)}")
    for i, m in enumerate(trimmed_messages):
        print(f"  [{i}] {m.type}: {m.content}")
    response = model.invoke(trimmed_messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("bot", call_model_with_trimming)
builder.add_edge(START, "bot")
builder.add_edge("bot", END)
graph = builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    config: RunnableConfig = {"configurable": {"thread_id": "qwen_trim_test"}}
    questions = [
        "我叫 Alice，今年 28 岁，住在上海。",
        "我有一只叫 Luna 的猫，今年三岁。",
        "Luna 最喜欢吃金枪鱼罐头，最讨厌洗澡。",
        "我平时喜欢读科幻小说和爬山。",
        "我的猫叫什么名字？我叫什么？",
    ]
    for q in questions:
        print(f"\nUser: {q}")
        res = graph.invoke({"messages": [HumanMessage(content=q)]}, config)
        print(f"Qwen: {res['messages'][-1].content}")
