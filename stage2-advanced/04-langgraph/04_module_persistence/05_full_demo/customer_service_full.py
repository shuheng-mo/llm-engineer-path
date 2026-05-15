"""完整实战 — Postgres Checkpointer + Postgres Store + 异步客服

对应课程章节：模块四 / 7.3 完整案例
"""

import asyncio
import os
import pathlib
import sys
import uuid
from typing import cast

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, MessagesState, START, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.postgres.aio import AsyncPostgresStore
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()

DB_URI = os.getenv("DB_URI")
if not DB_URI:
    raise RuntimeError(
        "请在 .env 中配置 DB_URI，例如 postgresql://user:pass@localhost:5432/langgraph"
    )

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")

# autocommit=True 是必须的：PostgresSaver.setup() 中有 CREATE INDEX CONCURRENTLY，
#   不能跑在事务里；prepare_threshold=0 是 LangGraph 官方推荐写法；
#   row_factory=dict_row 让连接的泛型参数对齐 PostgresSaver 期待的 DictRow。
CONNECTION_KWARGS = {
    "autocommit": True,
    "prepare_threshold": 0,
    "row_factory": dict_row,
}


async def customer_service_bot(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    """智能客服主节点。store 通过 functools.partial 注入。"""
    configurable = config.get("configurable") or {}
    user_id = configurable["user_id"]
    item = await store.aget(("user_preferences", user_id), "settings")

    system_prompt = "你是一个专业的客服助手。"
    if item is not None:
        prefs = item.value  # Item.value 才是真正存的 dict
        lang = prefs.get("language", "zh-CN")
        tone = prefs.get("tone", "professional")
        system_prompt += f"\n请使用{lang}语言，保持{tone}风格。"

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": [response]}


def build_graph(checkpointer, store: BaseStore):
    async def node(state: MessagesState, config: RunnableConfig):
        return await customer_service_bot(state, config, store=store)

    builder = StateGraph(MessagesState)
    builder.add_node("customer_service", node)
    builder.add_edge(START, "customer_service")
    builder.add_edge("customer_service", END)
    return builder.compile(checkpointer=checkpointer, store=store)


async def repl(app, store: BaseStore) -> None:
    """简单的终端交互界面，用于手动测试持久化效果。

    命令：
      :new          —— 开启新会话（生成新的 thread_id）
      :user <id>    —— 切换 user_id（用于 Store 中读取用户偏好）
      :pref <lang> <tone>  —— 写入当前 user_id 的偏好到 Store
      :thread       —— 显示当前 thread_id / user_id
      :quit / :exit —— 退出
    其他输入将作为消息发送给客服 Bot。
    """
    thread_id = f"customer_{uuid.uuid4().hex[:8]}"
    user_id = "user_demo"
    print("智能客服已启动。输入 :help 查看命令，:quit 退出。")
    print(f"当前会话: thread_id={thread_id}, user_id={user_id}\n")

    loop = asyncio.get_running_loop()
    while True:
        try:
            text = await loop.run_in_executor(None, input, "你 > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        text = text.strip()
        if not text:
            continue

        if text in (":quit", ":exit"):
            break
        if text == ":help":
            print(repl.__doc__)
            continue
        if text == ":new":
            thread_id = f"customer_{uuid.uuid4().hex[:8]}"
            print(f"[已开启新会话] thread_id={thread_id}\n")
            continue
        if text == ":thread":
            print(f"[当前] thread_id={thread_id}, user_id={user_id}\n")
            continue
        if text.startswith(":user "):
            user_id = text.split(maxsplit=1)[1].strip()
            print(f"[已切换] user_id={user_id}\n")
            continue
        if text.startswith(":pref "):
            parts = text.split()
            if len(parts) < 3:
                print("用法: :pref <language> <tone>，例如 :pref zh-CN friendly\n")
                continue
            await store.aput(
                ("user_preferences", user_id),
                "settings",
                {"language": parts[1], "tone": parts[2]},
            )
            print(f"[已写入偏好] user={user_id} language={parts[1]} tone={parts[2]}\n")
            continue

        config: RunnableConfig = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        result = await app.ainvoke({"messages": [HumanMessage(content=text)]}, config=config)
        print(f"客服 > {result['messages'][-1].content}\n")


async def main() -> None:
    assert DB_URI is not None  # 上面已校验，这里只是给 Pylance 做类型收窄
    async with AsyncConnectionPool(
        conninfo=DB_URI, min_size=2, max_size=10, kwargs=CONNECTION_KWARGS
    ) as raw_pool:
        # AsyncConnectionPool 的泛型参数 Pylance 无法从 kwargs 推断，手动 cast。
        pool = cast(AsyncConnectionPool[AsyncConnection[DictRow]], raw_pool)
        checkpointer = AsyncPostgresSaver(pool)
        store = AsyncPostgresStore(pool)
        # 首次运行时建表（异步版的 setup 必须 await）
        await checkpointer.setup()
        await store.setup()

        app = build_graph(checkpointer, store)
        await repl(app, store)


if __name__ == "__main__":
    asyncio.run(main())  # [当前] thread_id=customer_016e738d, user_id=user_demo
