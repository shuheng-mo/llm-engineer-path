"""Subagents — Step 1：定义底层业务工具

对应课程章节：模块六 / 二 / Step 1
"""

from langchain.tools import tool


@tool
def create_product(name: str, category: str, price: float, inventory: int) -> str:
    """创建新商品并上架。"""
    return f"商品已上架 - 名称: {name}, 类目: {category}, 价格: ¥{price}, 库存: {inventory}件"


@tool
def update_inventory(sku: str, quantity: int) -> str:
    """更新商品库存数量。"""
    return f"库存已更新 - SKU: {sku}, 新库存: {quantity}件"


@tool
def get_product_analytics(sku: str) -> str:
    """获取商品销售数据分析。"""
    return f"商品 {sku} 数据 - 浏览量: 1234, 销量: 45, 转化率: 3.6%"


@tool
def create_promotion(name: str, promotion_type: str, rules: str) -> str:
    """创建促销活动。"""
    return f"促销已创建 - 名称: {name}, 类型: {promotion_type}, 规则: {rules}"


@tool
def send_marketing_push(title: str, target_audience: str, channel: str) -> str:
    """发送营销推送消息。"""
    return f"推送已发送 - 标题: {title}, 渠道: {channel}, 目标: {target_audience}"
