"""ToolRuntime — 访问 Store（长期记忆）

对应课程章节：模块三 / 1.2.5

Store 是 LangGraph 的「**跨会话长期记忆**」：
- 与 Checkpointer 不同——Checkpointer 按 thread_id 存某次会话的 State 快照；
  Store 按 namespace + key 存**跨会话共享**的事实（用户画像、知识、偏好）。
- 工具里通过 `runtime.store` 访问，框架会自动把创建 agent 时传入的 store 注入。
"""

import pathlib
import sys
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langgraph.store.memory import InMemoryStore

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


@dataclass
class UserContext:
    """当前登录用户——和 Store 的 namespace 配合实现 per-user 记忆隔离。"""

    user_id: str


def _ns(user_id: str) -> tuple[str, str]:
    """每个用户的 Store namespace：("users", "<user_id>")"""
    return ("users", user_id)


@tool
def save_user_profile(name: str, age: int, runtime: ToolRuntime[UserContext]) -> str:
    """保存当前用户的个人画像（姓名、年龄）。"""
    assert runtime.store is not None, "agent 必须配置 store=... 才能用本工具"
    user_id = runtime.context.user_id
    runtime.store.put(_ns(user_id), "profile", {"name": name, "age": age})
    return f"已保存 {user_id} 的画像：{name}, {age} 岁"


@tool
def get_user_profile(runtime: ToolRuntime[UserContext]) -> str:
    """查询当前用户已保存的画像。"""
    assert runtime.store is not None, "agent 必须配置 store=... 才能用本工具"
    user_id = runtime.context.user_id
    item = runtime.store.get(_ns(user_id), "profile")
    if item is None:
        return f"{user_id} 暂无画像信息"
    return f"{user_id} 的画像：{item.value}"


# 进程级共享的长期记忆——所有 invoke 共享同一份 store
store = InMemoryStore()

agent = create_agent(
    model=model,
    tools=[save_user_profile, get_user_profile],
    system_prompt=(
        "你是一个会记住用户信息的助手。当用户告诉你他的姓名/年龄时，"
        "用 save_user_profile 工具保存；当用户问'还记得我吗'时，用 "
        "get_user_profile 工具查询。"
    ),
    context_schema=UserContext,
    store=store,
)


def _ask(user_id: str, message: str) -> None:
    print(f"\n→ [{user_id}] {message}")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        context=UserContext(user_id=user_id),
    )
    print(f"← {result['messages'][-1].content}")


if __name__ == "__main__":
    # 1. user_a 第一次告诉助手自己的信息 —— 写入 store
    _ask("user_a", "我叫张三，今年 28 岁")

    # 2. user_b 也告诉助手自己的信息 —— 不会污染 user_a 的记忆
    _ask("user_b", "我叫李四，今年 35 岁")

    # 3. user_a 重新提问 —— 应当能从 store 里把"张三, 28"读回来
    _ask("user_a", "你还记得我是谁吗？")

    # 4. 直接查 store 验证两人的画像被隔离存储
    print("\n=== Store 内容快照 ===")
    for user in ("user_a", "user_b"):
        item = store.get(("users", user), "profile")
        print(f"  ('users', {user!r}) / 'profile' → {item.value if item else None}")
