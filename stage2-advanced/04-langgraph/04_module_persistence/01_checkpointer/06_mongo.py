"""MongoDBSaver — 用 MongoDB 持久化 Checkpoint

对应课程章节：模块四 / 2.3.4

依赖:
    uv pip install langgraph-checkpoint-mongodb pymongo

MongoDB 适合「文档型 + 灵活 schema + 需要按字段查询历史」的场景。
和 Postgres 相比：没有 ACID 事务保证，但写入更轻、JSON 原生友好。
"""

import os
import pathlib
import sys
from typing import Annotated

from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pymongo import MongoClient
from typing_extensions import TypedDict

load_dotenv()

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-turbo", temperature=0.3)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [model.invoke(state.get("messages"))]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGO_URI)

# MongoDBSaver 可以传 db_name 指定 LangGraph 用哪个 database
checkpointer = MongoDBSaver(mongo_client, db_name="langgraph")
graph = builder.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "mongo_user_001"}}

print("--- MongoDB 对话 ---")
result = graph.invoke({"messages": [("user", "你好，Mongo!")]}, config)
print(f"Bot: {result['messages'][-1].content}")

# 第二轮 —— 跨 invoke 加载历史
result2 = graph.invoke({"messages": [("user", "我刚才说了什么？")]}, config)
print(f"Bot2: {result2['messages'][-1].content}")

# 验证落库：MongoDBSaver 默认把 checkpoint 写到集合 checkpoints / checkpoint_writes
db = mongo_client["langgraph"]
print(f"\ncollections: {db.list_collection_names()}")
print(f"checkpoints count: {db['checkpoints'].count_documents({})}")
