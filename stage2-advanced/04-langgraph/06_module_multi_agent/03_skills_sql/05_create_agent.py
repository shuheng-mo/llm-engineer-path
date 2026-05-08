"""Skills — Step 5：创建 SQL 助手 Agent

对应课程章节：模块六 / 四 / Step 5
"""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langgraph.checkpoint.memory import InMemorySaver

# from .04_skill_middleware import SkillMiddleware

load_dotenv()

model = ChatTongyi(model="qwen-max", api_key=os.getenv("DASHSCOPE_API_KEY"))

agent = create_agent(
    model,
    system_prompt="你是一个SQL查询助手，帮助用户编写业务数据库查询。",
    middleware=[SkillMiddleware()],                # noqa: F821
    checkpointer=InMemorySaver(),
)
