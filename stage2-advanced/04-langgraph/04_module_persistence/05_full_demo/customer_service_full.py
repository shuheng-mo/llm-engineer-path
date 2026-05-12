"""完整实战 — Postgres Checkpointer + Postgres Store + 异步客服

对应课程章节：模块四 / 7.3 完整案例
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, MessagesState, START, StateGraph
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool

load_dotenv()

DB_URI = os.getenv("DB_URI")
model = ChatOpenAI(model="gpt-4")

pool = ConnectionPool(conninfo=DB_URI, min_size=5, max_size=20)
checkpointer = PostgresSaver(pool)
store = PostgresStore.from_conn_string(DB_URI)

# 首次运行时建表
checkpointer.setup()
store.setup()


async def customer_service_bot(state: MessagesState):
    """智能客服主节点"""
    user_id = state["config"]["configurable"]["user_id"]
    preferences = await store.get(("user_preferences", user_id), "settings")

    system_prompt = "你是一个专业的客服助手。"
    if preferences:
        lang = preferences.get("language", "zh-CN")
        tone = preferences.get("tone", "professional")
        system_prompt += f"\n请使用{lang}语言，保持{tone}风格。"

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("customer_service", customer_service_bot)
builder.add_edge(START, "customer_service")
builder.add_edge("customer_service", END)

app = builder.compile(checkpointer=checkpointer, store=store)


# 使用示例
# config = {"configurable": {"thread_id": "customer_001", "user_id": "user_123"}}
# response1 = await app.ainvoke({"messages": [("user", "你好，我想咨询订单问题")]}, config=config)
# response2 = await app.ainvoke({"messages": [("user", "我的订单号是 12345")]}, config=config)
# response3 = await app.ainvoke({"messages": [("user", "我刚才说的订单号是多少？")]}, config=config)
