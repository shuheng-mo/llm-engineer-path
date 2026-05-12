"""ToolRuntime — 访问 Store（长期记忆）

对应课程章节：模块三 / 1.2.5
"""

from langchain.tools import ToolRuntime, tool


@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """查询用户信息"""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "用户不存在"


@tool
def save_user_info(user_id: str, name: str, age: int, runtime: ToolRuntime) -> str:
    """保存用户信息"""
    store = runtime.store
    store.put(("users",), user_id, {"name": name, "age": age})
    return "保存成功"


# 使用
# store = InMemoryStore()
# agent = create_agent(model=model, tools=[get_user_info, save_user_info], store=store)
