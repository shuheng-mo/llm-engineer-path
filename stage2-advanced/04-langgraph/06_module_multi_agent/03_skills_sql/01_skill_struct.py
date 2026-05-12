"""Skills — Step 1：定义技能结构（name + description + content）

对应课程章节：模块六 / 四 / Step 1
"""

from typing import TypedDict


class Skill(TypedDict):
    """可以渐进式披露的技能。

    description 显示在系统提示词中（让 LLM 知道有哪些可加载技能）；
    content 是完整内容，按需通过工具加载。
    """

    name: str
    description: str
    content: str
