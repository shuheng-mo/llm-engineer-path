"""ToolRuntime — 访问 Context（运行时配置）

对应课程章节：模块三 / 1.2.4

Context 是「**调用 invoke 时传入、对工具可见、但 LLM 看不到**」的一份运行时配置。
典型用途：当前用户 id、租户 id、API key、feature flag —— 这些不应出现在
prompt 里、但工具需要用来查数据 / 鉴权 / 计费。
"""

import pathlib
import sys
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


@dataclass
class UserContext:
    """每次 invoke 时由调用方注入的运行时上下文。"""

    user_id: str
    api_key: str  # 演示字段：真实场景下用来调外部 API


# 模拟的"账户系统"——真实场景下这里会走 HTTP / DB
_FAKE_ACCOUNTS = {
    "user_123": {"balance": 5000, "currency": "CNY"},
    "user_456": {"balance": 128, "currency": "USD"},
}


@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """获取当前登录用户的账户余额。"""
    user_id = runtime.context.user_id
    # 演示如何拿到 api_key（注意：不要把它返回给 LLM）
    # api_key = runtime.context.api_key

    account = _FAKE_ACCOUNTS.get(user_id)
    if account is None:
        return f"未找到用户 {user_id} 的账户"
    return f"用户 {user_id} 的账户余额：{account['balance']} {account['currency']}"


agent = create_agent(
    model=model,
    tools=[get_account_info],
    system_prompt="你是一个友好的账户助手，可以为登录用户查询账户余额。",
    context_schema=UserContext,
)


if __name__ == "__main__":
    # 同一份代码，不同的 context 注入 → 工具看到不同的 user_id
    for user in ("user_123", "user_456", "user_999"):
        print(f"\n=== 模拟登录用户：{user} ===")
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "查一下我的账户余额"}]},
            context=UserContext(user_id=user, api_key="sk-demo"),
        )
        print(result["messages"][-1].content)
