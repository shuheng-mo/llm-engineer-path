"""Hello World — 最简 StateGraph + MessagesState

对应课程章节：模块一 / 4.1
"""

import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

llm = ChatTongyi(
    model="qwen-turbo",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
    top_p=0.9,
)


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
