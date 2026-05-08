"""Skills — Step 4：SkillMiddleware（在 system prompt 注入技能列表）

对应课程章节：模块六 / 四 / Step 4
"""
from typing import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage

# from .02_skills_definitions import SKILLS
# from .03_load_skill_tool import load_skill


class SkillMiddleware(AgentMiddleware):
    """将技能描述注入系统提示词的中间件"""

    tools = [load_skill]                                          # noqa: F821

    def __init__(self):
        skills_list = []
        for skill in SKILLS:                                       # noqa: F821
            skills_list.append(f"- **{skill['name']}**: {skill['description']}")
        self.skills_prompt = "\n".join(skills_list)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        skills_addendum = (
            f"\n\n## 可用技能\n\n{self.skills_prompt}\n\n"
            "当你需要处理特定类型请求的详细信息时，使用 load_skill 工具。"
        )

        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum},
        ]
        new_system_message = SystemMessage(content=new_content)

        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)
