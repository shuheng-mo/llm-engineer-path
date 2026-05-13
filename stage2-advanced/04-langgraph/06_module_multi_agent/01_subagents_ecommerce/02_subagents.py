"""Subagents — Step 2：用 create_agent 创建 product 和 marketing 两个专家子 Agent

对应课程章节：模块六 / 二 / Step 2
"""

import pathlib
import sys

from langchain.agents import create_agent

# from .01_tools import create_product, update_inventory, get_product_analytics
# from .01_tools import create_promotion, send_marketing_push

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


product_agent = create_agent(
    model,
    tools=[create_product, update_inventory, get_product_analytics],  # noqa: F821
    system_prompt="""你是电商商品管理专家。

    职责：
    - 创建和上架新商品
    - 管理商品库存
    - 分析商品销售数据

    工作原则：
    ✓ 确保商品信息完整准确
    ✓ 在最终消息中包含所有操作结果""",
)


marketing_agent = create_agent(
    model,
    tools=[create_promotion, send_marketing_push],  # noqa: F821
    system_prompt="""你是电商营销推广专家。

    职责：
    - 创建各类促销活动
    - 制定营销推送策略

    工作原则：
    ✓ 活动规则清晰易懂
    ✓ 在最终消息中包含所有操作结果""",
)
