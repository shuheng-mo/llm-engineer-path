"""create_agent + Checkpointer — 多轮对话短期记忆

对应课程章节：模块三 / 2.3.1
"""

import pathlib
import sys

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model, get_time, get_weather  # noqa: E402

model = get_chat_model("qwen-max")

tools = [get_weather, get_time]

memory = MemorySaver()

agent = create_agent(
    model=model,  # noqa: F821
    tools=tools,  # noqa: F821
    checkpointer=memory,
)

config = {"configurable": {"thread_id": "user_123"}}

# 第一轮
agent.invoke({"messages": [{"role": "user", "content": "我叫张三"}]}, config=config)

# 第二轮 — Agent 能记住上下文
response = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫什么名字？"}]}, config=config
)
print(response["messages"][-1].content)  # 您叫张三。
