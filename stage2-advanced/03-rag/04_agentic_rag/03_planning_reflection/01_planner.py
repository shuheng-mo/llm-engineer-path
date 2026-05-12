"""Planner — 用 with_structured_output 把目标拆成步骤列表

对应课程章节：四 / 第三章 2.3
"""

import os
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class Plan(BaseModel):
    """任务的步骤列表。"""

    steps: List[str] = Field(description="解决问题所需的具体步骤列表")


llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专家级的任务规划器。给定一个复杂的目标，将其拆解为一步步可执行的子任务。",
        ),
        ("user", "目标: {objective}"),
    ]
)

planner = planner_prompt | llm.with_structured_output(Plan)


if __name__ == "__main__":
    plan = planner.invoke(
        {
            "objective": "分析比亚迪和特斯拉2024年Q3的净利润差异，并结合当前股市情绪给出投资风险提示。",
        }
    )
    print(plan.steps)
