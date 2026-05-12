"""InMemorySaver 基础用法 — 编译时传 checkpointer

对应课程章节：模块四 / 2.2.1
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, START, StateGraph

load_dotenv()

checkpointer = MemorySaver()

model = ChatOpenAI(
    model=os.getenv("QWEN_MODEL_NLP", "qwen-max"),
    base_url=os.getenv("QWEN_BASE_URL"),
    api_key=os.getenv("QWEN_API_KEY"),
    temperature=0.3,
)


def chatbot(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chatbot)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile(checkpointer=checkpointer)
