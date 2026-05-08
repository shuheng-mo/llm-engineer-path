"""Subagents — Step 2：用 create_agent 创建 product 和 marketing 两个专家子 Agent

对应课程章节：模块六 / 二 / Step 2
"""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi

# from .01_tools import create_product, update_inventory, get_product_analytics
# from .01_tools import create_promotion, send_marketing_push

load_dotenv()

model = ChatTongyi(model="qwen-max", api_key=os.getenv("DASHSCOPE_API_KEY"))


product_agent = create_agent(
    model,
    tools=[create_product, update_inventory, get_product_analytics],   # noqa: F821
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
    tools=[create_promotion, send_marketing_push],     # noqa: F821
    system_prompt="""你是电商营销推广专家。

    职责：
    - 创建各类促销活动
    - 制定营销推送策略

    工作原则：
    ✓ 活动规则清晰易懂
    ✓ 在最终消息中包含所有操作结果""",
)
