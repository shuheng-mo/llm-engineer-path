"""ToolRuntime — 访问 Context（运行时配置）

对应课程章节：模块三 / 1.2.4
"""

from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool


@dataclass
class UserContext:
    user_id: str
    api_key: str


@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """获取账户信息"""
    user_id = runtime.context.user_id
    # api_key = runtime.context.api_key  # 用 api_key 调外部 API
    return f"用户 {user_id} 的账户余额：5000 元"


# 使用：创建 Agent 时通过 context_schema 声明 context 类型
# agent = create_agent(model=model, tools=[get_account_info], context_schema=UserContext)
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "查询我的余额"}]},
#     context=UserContext(user_id="user_123", api_key="sk-xxx"),
# )
