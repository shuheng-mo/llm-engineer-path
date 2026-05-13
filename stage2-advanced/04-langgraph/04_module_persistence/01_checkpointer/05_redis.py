"""RedisSaver — 用 Redis 持久化 Checkpoint

对应课程章节：模块四 / 2.3.3

依赖:
uv pip install langgraph-checkpoint-redis redis
"""

import os
import pathlib
import sys
from typing import Annotated

import redis
from dotenv import load_dotenv
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max", temperature=0.3)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [model.invoke(state.get("messages"))]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=12,
    password=os.getenv("REDIS_PASSWORD"),
    # decode_responses=False —— LangGraph 序列化通常是二进制
)

checkpointer = RedisSaver(redis_client=redis_client)
graph = builder.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "redis_user_999"}}

print("--- Redis 对话 ---")
result = graph.invoke({"messages": [("user", "Redis 准备好了吗？")]}, config)
print(f"Bot: {result['messages'][-1].content}")

print(f"Key 数量: {len(redis_client.keys('checkpoint:*'))}")
