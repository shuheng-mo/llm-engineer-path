"""Subagents — Step 3：把子 Agent 包装为工具（Command 跨节点写状态）

对应课程章节：模块六 / 二 / Step 3
"""

from typing import Annotated

from langchain.tools import InjectedToolCallId, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

# from .02_subagents import product_agent, marketing_agent


@tool(
    "manage_product",
    description="""商品管理专家。

    何时调用：
    - 用户需要上架、修改或下架商品
    - 涉及库存管理和调整
    - 需要商品销售数据分析

    输入：自然语言描述的商品管理需求
    示例："上架一款夏季新款连衣裙，价格299元""",
)
def manage_product(
    request: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """调用商品管理专家 Agent。

    InjectedToolCallId 让框架自动塞入当前工具调用的 id（不用 LLM 传）。
    """
    result = product_agent.invoke({"messages": [{"role": "user", "content": request}]})  # noqa: F821
    final_message = result["messages"][-1].content

    return Command(
        update={
            "messages": [ToolMessage(content=final_message, tool_call_id=tool_call_id)],
        }
    )


@tool(
    "create_campaign",
    description="""营销推广专家。

    何时调用：
    - 用户需要创建促销活动
    - 需要发送营销推送

    输入：自然语言描述的营销需求
    示例："创建618大促满减活动""",
)
def create_campaign(
    request: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """调用营销推广专家 Agent"""
    result = marketing_agent.invoke({"messages": [{"role": "user", "content": request}]})  # noqa: F821
    final_message = result["messages"][-1].content

    return Command(
        update={
            "messages": [ToolMessage(content=final_message, tool_call_id=tool_call_id)],
        }
    )
