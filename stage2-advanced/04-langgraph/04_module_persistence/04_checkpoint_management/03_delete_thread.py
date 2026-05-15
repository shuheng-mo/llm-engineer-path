"""策略 4：删除整条线程（Delete Thread）— 根据 thread_id 清空全部历史

与 `02_remove_messages.py` 的区别：
- RemoveMessage 在「图运行内」物理删除消息，但 checkpoint 本身仍然保留在
  checkpointer 中（每一步都会写新版本）。
- `checkpointer.delete_thread(thread_id)` 是在「图运行外」的运维操作，
  直接把这条线程在 checkpointer 里的所有 checkpoints / writes 全部抹掉，
  相当于让该 thread_id 回到「从未对话过」的状态。

对应课程章节：模块四 / 4.5（补充）
"""

import pathlib
import sys

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


def chat_node(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}


checkpointer = MemorySaver()
builder = StateGraph(MessagesState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=checkpointer)


def show_history(thread_id: str) -> None:
    cfg: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(cfg)
    msgs = snapshot.values.get("messages", []) if snapshot.values else []
    print(f"  [thread={thread_id}] 当前 checkpoint 中消息数 = {len(msgs)}")
    for i, m in enumerate(msgs):
        print(f"    [{i}] {m.type}: {m.content}")


if __name__ == "__main__":
    thread_id = "qwen_delete_thread_test"
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    print("=== 1. 累积几轮对话 ===")
    for q in [
        "我叫 Alice，我有一只叫 Luna 的猫。",
        "Luna 喜欢吃金枪鱼罐头。",
        "我的猫叫什么名字？",
    ]:
        print(f"\nUser: {q}")
        res = graph.invoke({"messages": [HumanMessage(content=q)]}, config)
        print(f"Qwen: {res['messages'][-1].content}")

    print("\n=== 2. 删除前的历史 ===")
    show_history(thread_id)

    print("\n=== 3. 调用 checkpointer.delete_thread() ===")
    checkpointer.delete_thread(thread_id)
    print(f"  已删除 thread_id={thread_id} 的全部 checkpoint")

    print("\n=== 4. 删除后再次查看 ===")
    show_history(thread_id)

    print("\n=== 5. 同一 thread_id 再次提问，模型已不记得 Alice / Luna ===")
    q = "我叫什么？我的猫叫什么？"
    print(f"\nUser: {q}")
    res = graph.invoke({"messages": [HumanMessage(content=q)]}, config)
    print(f"Qwen: {res['messages'][-1].content}")
