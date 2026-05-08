"""Subagents — 2.4 添加人机协同：HumanInTheLoopMiddleware

对应课程章节：模块六 / 二 / 2.4
"""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

# from .02_subagents import model, create_product, update_inventory, get_product_analytics

# 子 Agent 加审批中间件
product_agent = create_agent(
    model,                                                           # noqa: F821
    tools=[create_product, update_inventory, get_product_analytics],  # noqa: F821
    system_prompt="PRODUCT_PROMPT 占位",
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_product": True},
            description_prefix="📦 商品上架待审批",
        ),
    ],
)

# Supervisor 需要 checkpointer 才能暂停/恢复
supervisor = create_agent(
    model,                                              # noqa: F821
    tools=[manage_product, create_campaign],            # noqa: F821
    system_prompt="SUPERVISOR_PROMPT 占位",
    checkpointer=InMemorySaver(),
)
