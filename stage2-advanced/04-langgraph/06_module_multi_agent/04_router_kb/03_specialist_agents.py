"""Router — Step 3：三个专业 Agent（github / notion / slack）

对应课程章节：模块六 / 五 / Step 3
"""

import pathlib
import sys

from langchain.agents import create_agent

# from .02_tools import (
#     search_code, search_issues, search_notion, get_page, search_slack, get_thread,
# )

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


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
