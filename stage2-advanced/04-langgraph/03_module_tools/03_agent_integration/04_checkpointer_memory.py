"""create_agent + Checkpointer — 多轮对话短期记忆

对应课程章节：模块三 / 2.3.1
"""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

# 假设已经有 model 和 tools
# from .01_create_agent import model
# tools = []

memory = MemorySaver()

agent = create_agent(
    model=model,                # noqa: F821
    tools=tools,                # noqa: F821
    checkpointer=memory,
)

config = {"configurable": {"thread_id": "user_123"}}

# 第一轮
agent.invoke({"messages": [{"role": "user", "content": "我叫张三"}]}, config=config)

# 第二轮 — Agent 能记住上下文
response = agent.invoke({"messages": [{"role": "user", "content": "我叫什么名字？"}]}, config=config)
print(response["messages"][-1].content)        # 您叫张三。
