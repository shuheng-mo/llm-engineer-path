"""Store 基础操作 — put / get / search

对应课程章节：模块四 / 3.2.1
"""

from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# 存储数据（用 namespace 组织）
store.put(
    namespace=("user_preferences", "user_123"),
    key="language",
    value={"lang": "zh-CN", "tone": "professional"},
)

# 检索单条
preference = store.get(("user_preferences", "user_123"), "language")
print(f"prefernce: {preference}")

# 列出所有 key
keys = store.search(("user_preferences", "user_123"))
print(f"desired key: {keys}")
