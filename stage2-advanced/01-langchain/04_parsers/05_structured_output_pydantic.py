"""with_structured_output(pydantic) — 推荐方式

对应课程章节：第五章 / 3.1
"""
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"


class Product(BaseModel):
    name: str = Field(description="商品名称，英文键名：name")
    price: float = Field(description="商品价格（元），英文键名：price")
    stock: int = Field(description="库存数量，英文键名：stock")
    category: Optional[str] = Field(default=None, description="商品分类")


class OrderInfo(BaseModel):
    order_id: str = Field(description="订单编号（如：ORD-2025001）")
    user_name: str = Field(description="用户名")
    products: List[Product] = Field(description="订单包含的商品列表")
    total_amount: float = Field(description="订单总金额（元）")
    status: str = Field(description="订单状态：pending/paid/shipped/delivered")


base_model = ChatOpenAI(
    model="qwen-plus",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0,
)

structured_model = base_model.with_structured_output(
    schema=OrderInfo,
    method="json_mode",
    include_raw=False,
)

input_text = """
请严格按照以下要求提取订单信息并输出 JSON 格式：
1. JSON 字段名必须使用英文，且严格匹配：order_id、user_name、products、total_amount、status；
2. products 是数组，每个元素包含：name、price、stock；
3. status 取值只能是：pending/paid/shipped/delivered；
4. 只输出 JSON，不要其他内容。

待提取的订单信息：
用户张三下单购买了2件T恤（价格99元/件，库存100件）和1双鞋子（价格299元，库存50件），
订单编号是ORD-2025001，总金额497元，目前订单状态为已支付。
"""

result = structured_model.invoke(input_text)

print("=== 结构化订单信息 ===")
print(f"订单编号：{result.order_id}")
print(f"用户名：{result.user_name}")
print(f"订单状态：{result.status}")
print(f"总金额：{result.total_amount} 元")
print("\n=== 商品列表 ===")
for idx, product in enumerate(result.products, 1):
    print(f"{idx}. 商品：{product.name} | 价格：{product.price} 元 | 库存：{product.stock} 件")
