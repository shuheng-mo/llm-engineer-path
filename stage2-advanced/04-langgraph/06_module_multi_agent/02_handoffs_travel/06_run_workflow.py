"""Handoffs — Step 6：测试完整工作流（4 轮对话）

对应课程章节：模块六 / 三 / Step 6
"""
import uuid

# from .05_create_agent import travel_agent

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("=== 第1轮 ===")
result = travel_agent.invoke(                                # noqa: F821
    {"messages": [{"role": "user", "content": "我想规划一次旅行"}]}, config)
print(result["messages"][-1].content)

print("\n=== 第2轮 ===")
result = travel_agent.invoke(                                # noqa: F821
    {"messages": [{"role": "user", "content": "预算中等舒适型，想体验文化，7月初出发玩5天"}]}, config)
print(result["messages"][-1].content)

print("\n=== 第3轮 ===")
result = travel_agent.invoke(                                # noqa: F821
    {"messages": [{"role": "user", "content": "我选择去西安"}]}, config)
print(result["messages"][-1].content)

print("\n=== 第4轮 ===")
result = travel_agent.invoke(                                # noqa: F821
    {"messages": [{"role": "user", "content": "帮我制定详细行程"}]}, config)
print(result["messages"][-1].content)
