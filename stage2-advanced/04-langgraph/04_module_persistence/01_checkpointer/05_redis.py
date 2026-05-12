"""RedisSaver — 用 Redis 持久化 Checkpoint

对应课程章节：模块四 / 2.3.3

依赖:
uv pip install langgraph-checkpoint-redis redis
"""

import os
from typing import Annotated

import redis
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
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
