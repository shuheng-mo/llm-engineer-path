"""Skills — Step 3：load_skill 工具（按需加载技能内容）

对应课程章节：模块六 / 四 / Step 3
"""

from langchain.tools import tool

# from .02_skills_definitions import SKILLS


@tool
def load_skill(skill_name: str) -> str:
    """加载技能的完整内容到 Agent 上下文中。

    当你需要关于如何处理特定类型请求的详细信息时使用此工具。
    这将为你提供该技能领域的全面说明、策略和指南。

    Args:
        skill_name: 要加载的技能名称（如 "sales_analytics", "inventory_management"）
    """
    for skill in SKILLS:  # noqa: F821
        if skill["name"] == skill_name:
            return f"✅ 已加载技能：{skill_name}\n\n{skill['content']}"

    available = ", ".join(s["name"] for s in SKILLS)  # noqa: F821
    return f"❌ 技能 '{skill_name}' 未找到。可用技能：{available}"
