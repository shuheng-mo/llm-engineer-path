"""Router — Step 1：定义状态（input / classifications / results / final）

对应课程章节：模块六 / 五 / Step 1
"""
import operator
from typing import Annotated, Literal, TypedDict


class AgentInput(TypedDict):
    query: str


class AgentOutput(TypedDict):
    source: str
    result: str


class Classification(TypedDict):
    source: Literal["github", "notion", "slack"]
    query: str


class RouterState(TypedDict):
    query: str
    classifications: list[Classification]
    results: Annotated[list[AgentOutput], operator.add]
    final_answer: str
