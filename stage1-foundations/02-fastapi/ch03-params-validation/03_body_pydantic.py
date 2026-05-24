"""3.3 请求体 + Pydantic 模型"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# 1. 定义数据模型
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None  # 可选字段，默认为 None
    description: Optional[str] = None  # 将模型作为类型提示用于参数
    tax: Optional[float] = None
    price_with_tax: Optional[float] = None


@app.post("/items/")
async def create_item(item: Item):  # item 此时已经是 Item 类的实例，拥有属性提示
    item_dict = (
        item.model_dump()
    )  # 这一步就是把复杂的 Pydantic 对象转成简单的字典，以便 FastAPI 自动处理和返回。
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
        # item_dict["price_with_tax"] = price_with_tax
    return item_dict
