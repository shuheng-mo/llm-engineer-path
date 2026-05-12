"""查看线程状态 — graph.get_state(config)

对应课程章节：模块四 / 5.1
"""

config = {
    "configurable": {
        "thread_id": "session_user_123",
        # 可选：指定特定 checkpoint
        # "checkpoint_id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
    }
}

# state = graph.get_state(config)        # noqa: F821
# print(state)

# 返回结果示例：
# StateSnapshot(
#     values={"messages": [HumanMessage(...), AIMessage(...), ...]},
#     next=(),
#     config={"configurable": {"thread_id": "session_user_123", ...}},
#     metadata={"source": "loop", "step": 4, ...},
#     created_at="2025-05-05T16:01:24.680462+00:00",
# )
