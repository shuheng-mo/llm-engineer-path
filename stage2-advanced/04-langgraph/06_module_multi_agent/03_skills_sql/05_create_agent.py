"""Skills — Step 5：创建 SQL 助手 Agent

对应课程章节：模块六 / 四 / Step 5
"""

import pathlib
import sys

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# from .04_skill_middleware import SkillMiddleware

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")

agent = create_agent(
    model,
    system_prompt="你是一个SQL查询助手，帮助用户编写业务数据库查询。",
    middleware=[SkillMiddleware()],  # noqa: F821
    checkpointer=InMemorySaver(),
)
