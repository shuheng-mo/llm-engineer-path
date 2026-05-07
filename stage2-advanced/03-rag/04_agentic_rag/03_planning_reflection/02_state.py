"""LangGraph 状态设计 — Plan-and-Execute 风格

对应课程章节：四 / 第三章 3.1
"""
import operator
from typing import Annotated, List

from typing_extensions import TypedDict


class AgentState(TypedDict):
    objective: str                                              # 原始用户问题
    plan: List[str]                                             # 剩余的任务步骤
    past_steps: List[str]                                       # 已经完成的步骤及结果
    final_answer: str                                           # 最终答案
    scratchpad: Annotated[List[str], operator.add]              # 累积的中间思考过程
