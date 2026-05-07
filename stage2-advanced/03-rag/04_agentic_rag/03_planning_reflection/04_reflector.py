"""Reflector 节点 — 评估信息是否充足，不足则把建议步骤插队回 plan

对应课程章节：四 / 第三章 4.2
"""
from pydantic import BaseModel, Field


class ReflectionSchema(BaseModel):
    is_satisfactory: bool = Field(description="当前收集的信息是否足以回答用户问题")
    feedback: str = Field(description="如果不足，指出缺什么；如果足够，留空")
    next_step_suggestion: str = Field(description="如果不足，建议的一个补救步骤")


# reflector_runner = llm.with_structured_output(ReflectionSchema)   # 由外部注入 llm

MAX_REFLECTIONS = 5


def reflector_node(state):
    print("\n--- [3] Reflector: 反思与评估 ---")

    if state.get("reflection_count", 0) >= MAX_REFLECTIONS:
        print("    -> 反思次数过多，跳过反思，直接生成最终答案。")
        return {"scratchpad": "Reflection skipped due to max reflections"}

    context = "\n".join(state["past_steps"])
    prompt = f"""
    目标: {state['objective']}

    已获取的信息:
    {context}

    请判断信息是否充分？如果遇到"未找到数据"或信息矛盾，请标记为不满意。
    """
    reflection = reflector_runner.invoke(prompt)  # noqa: F821

    state["reflection_count"] = state.get("reflection_count", 0) + 1

    if reflection.is_satisfactory:
        print("    -> 评估通过：信息充足。")
        return {"scratchpad": "Reflection Passed"}

    print(f"    -> 评估未通过：{reflection.feedback}")
    new_plan = [reflection.next_step_suggestion] + state["plan"]
    return {"plan": new_plan, "scratchpad": f"Reflection Failed: {reflection.feedback}"}
