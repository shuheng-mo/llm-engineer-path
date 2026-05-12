"""Agent 反思循环 — 生成 → 评估 → 反思 → 改进 自循环图

对应课程章节：模块二 / 实践练习：Agent 反思循环
"""

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm = ChatTongyi(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
)


class ReflectionState(TypedDict):
    task: str
    draft: str
    quality_score: float
    reflection: str
    iteration: int
    max_iterations: int


def generate_draft(state: ReflectionState) -> dict:
    print(f"\n{'=' * 60}\nNode 1: 生成初稿 (第 {state['iteration'] + 1} 次)\n{'=' * 60}")
    task = state["task"]
    iteration = state["iteration"]

    if iteration == 0:
        prompt = f"请写一篇关于'{task}'的文章，大约150字左右。"
    else:
        prompt = f"""
请改进以下文章：

原文：
{state['draft']}

改进建议：
{state['reflection']}

请根据改进建议重写文章，保持150字左右。
"""

    response = llm.invoke(prompt)
    print(f"\n生成结果:\n{response.content}")
    return {"draft": response.content, "iteration": iteration + 1}


def evaluate_quality(state: ReflectionState) -> dict:
    print(f"\n{'=' * 60}\nNode 2: 评估质量\n{'=' * 60}")
    prompt = f"""
请评估以下文章的质量。

任务要求: 写一篇关于'{state['task']}'的文章
文章内容:
{state['draft']}

评估标准：
1. 内容完整性
2. 逻辑清晰度
3. 语言表达

请给出0-1的分数（保留两位小数），只输出数字，不要其他内容。
例如：0.75
"""
    response = llm.invoke(prompt)
    try:
        score = float(response.content.strip())
        score = max(0.0, min(1.0, score))
    except ValueError:
        print("⚠️  无法解析分数，使用默认值 0.5")
        score = 0.5
    print(f"\n质量分数: {score:.2f}")
    return {"quality_score": score}


def reflect_and_improve(state: ReflectionState) -> dict:
    print(f"\n{'=' * 60}\nNode 3: 反思改进\n{'=' * 60}")
    prompt = f"""
请分析以下文章存在的问题，并给出具体的改进建议。

任务要求: 写一篇关于'{state['task']}'的文章
当前文章:
{state['draft']}

当前评分: {state['quality_score']:.2f}

请简要指出1-2个主要问题，并给出改进方向（50字以内）。
"""
    response = llm.invoke(prompt)
    print(f"\n改进建议:\n{response.content}")
    return {"reflection": response.content}


def should_continue(state: ReflectionState) -> Literal["reflect", "end"]:
    score = state["quality_score"]
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    print(f"\n{'=' * 60}\n条件判断: 是否继续改进\n{'=' * 60}")
    print(f"当前分数: {score:.2f}\n迭代次数: {iteration}/{max_iter}")

    if score >= 0.9:
        print("✅ 决策: 质量达标 (>= 0.9)，结束改进")
        return "end"
    if iteration >= max_iter:
        print("⚠️  决策: 达到最大迭代次数，停止改进")
        return "end"
    print("❌ 决策: 质量不足，继续改进")
    return "reflect"


def build_graph():
    builder = StateGraph(ReflectionState)
    builder.add_node("generate_draft", generate_draft)
    builder.add_node("evaluate_quality", evaluate_quality)
    builder.add_node("reflect", reflect_and_improve)

    builder.add_edge(START, "generate_draft")
    builder.add_edge("generate_draft", "evaluate_quality")
    builder.add_conditional_edges(
        source="evaluate_quality",
        path=should_continue,
        path_map={"reflect": "reflect", "end": END},
    )
    builder.add_edge("reflect", "generate_draft")
    return builder.compile()


def run_reflection_loop(task: str, max_iterations: int = 3):
    print("\n" + "=" * 60)
    print("反思循环 Agent 启动")
    print("=" * 60)
    print(f"任务: {task}\n最大迭代次数: {max_iterations}\n质量阈值: 0.9")

    graph = build_graph()
    initial_state = {
        "task": task,
        "draft": "",
        "quality_score": 0.0,
        "reflection": "",
        "iteration": 0,
        "max_iterations": max_iterations,
    }
    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("最终结果")
    print("=" * 60)
    print(f"总迭代次数: {final_state['iteration']}")
    print(f"最终质量分数: {final_state['quality_score']:.2f}")
    print(f"\n最终文章:\n{'-' * 60}\n{final_state['draft']}\n{'-' * 60}")
    return final_state


if __name__ == "__main__":
    run_reflection_loop(task="人工智能的发展历程", max_iterations=3)
