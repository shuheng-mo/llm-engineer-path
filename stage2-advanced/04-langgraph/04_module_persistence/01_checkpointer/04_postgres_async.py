"""AsyncPostgresSaver 异步版本（FastAPI 常用）

对应课程章节：模块四 / 2.3.2 异步
"""
import asyncio
import os
import sys
from typing import Annotated

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

if not os.getenv("DB_URI"):
    raise ValueError("请在 .env 文件中配置 DB_URI")

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


async def main():
    DB_URI = os.getenv("DB_URI")
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()

        graph = builder.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "async_pg_002"}}

        print("--- 异步 PostgreSQL 测试 ---")
        print("User: Hello Async DB")
        response1 = await graph.ainvoke({"messages": [("user", "Hello Async DB")]}, config)
        print(f"Bot: {response1['messages'][-1].content}")

        print("\nUser: 我刚才说了什么")
        response2 = await graph.ainvoke({"messages": [("user", "我刚才说了什么")]}, config)
        print(f"Bot: {response2['messages'][-1].content}")

        print("执行完成")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
