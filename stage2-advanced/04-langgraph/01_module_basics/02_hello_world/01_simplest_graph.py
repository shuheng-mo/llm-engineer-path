"""Hello World — 最简 StateGraph + MessagesState

对应课程章节：模块一 / 4.1
"""

import pathlib
import sys

from langgraph.graph import END, START, MessagesState, StateGraph

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

llm = get_chat_model("qwen-turbo", temperature=0.7, top_p=0.9)


def chat_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()  # 执行图验证优化并生成可执行的Pregel引擎实例

if __name__ == "__main__":
    result = graph.invoke({"messages": [{"role": "user", "content": "你好，请介绍一下 LangGraph"}]})
    print(result["messages"][-1].content)
