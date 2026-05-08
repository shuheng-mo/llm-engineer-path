"""PostgresSaver 同步版本 — 用 ConnectionPool 持久化到 Postgres

对应课程章节：模块四 / 2.3.2 同步

依赖:
uv pip install langgraph-checkpoint-postgres psycopg[binary,pool]
"""
import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from psycopg_pool import ConnectionPool
from typing_extensions import TypedDict

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("QWEN_MODEL_NLP", "qwen-max"),
    base_url=os.getenv("QWEN_BASE_URL"),
    api_key=os.getenv("QWEN_API_KEY"),
    temperature=0.3,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [model.invoke(state.get("messages"))]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


DB_URI = os.getenv("DB_URI")

with ConnectionPool(conninfo=DB_URI, min_size=1, max_size=10) as pool:
    checkpointer = PostgresSaver(pool)
    # 首次运行时取消下行注释建表（幂等）
    # checkpointer.setup()

    graph = builder.compile(checkpointer=checkpointer)

    thread_id = "postgres_user_001"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- 开始对话 (Thread: {thread_id}) ---")
    result = graph.invoke({"messages": [("user", "你好，Postgres!")]}, config)
    print(f"回复: {result['messages'][-1].content}")

    result2 = graph.invoke({"messages": [("user", "我刚才说了什么？")]}, config)
    print(f"回复2: {result2['messages'][-1].content}")
