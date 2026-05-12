"""Router — Step 3：三个专业 Agent（github / notion / slack）

对应课程章节：模块六 / 五 / Step 3
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi

# from .02_tools import (
#     search_code, search_issues, search_notion, get_page, search_slack, get_thread,
# )

load_dotenv()

model = ChatTongyi(model="qwen-max", api_key=os.getenv("DASHSCOPE_API_KEY"))


github_agent = create_agent(
    model,
    tools=[search_code, search_issues],  # noqa: F821
    system_prompt="你是GitHub专家。搜索代码、issue和PR回答问题。",
)

notion_agent = create_agent(
    model,
    tools=[search_notion, get_page],  # noqa: F821
    system_prompt="你是Notion专家。搜索文档回答问题。",
)

slack_agent = create_agent(
    model,
    tools=[search_slack, get_thread],  # noqa: F821
    system_prompt="你是Slack专家。搜索讨论回答问题。",
)
