"""Executor 节点 — 执行 plan[0]，把结果追加到 past_steps

对应课程章节：四 / 第三章 3.2
"""
# from .02_state import AgentState   # 实际项目可以这样 import


def search_tool(query: str):
    return f"Mock search result for: {query}"


def execute_step(state):
    plan = state["plan"]
    current_task = plan[0]

    # 真实场景：Agent 根据 current_task 决定调用哪个工具
    tool_result = search_tool(current_task)

    return {
        "past_steps": [f"Task: {current_task}, Result: {tool_result}"],
        "plan": plan[1:],
        "scratchpad": [f"Finished: {current_task}"],
    }
