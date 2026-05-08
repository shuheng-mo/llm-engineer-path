"""查看线程历史 — graph.get_state_history(config)

对应课程章节：模块四 / 5.2
"""
config = {"configurable": {"thread_id": "session_user_123"}}

# history = list(graph.get_state_history(config))   # noqa: F821
# for snapshot in history:
#     print(f"步骤 {snapshot.metadata['step']}: {snapshot.values['messages'][-1].content}")
