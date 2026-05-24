"""1.2 Pydantic 基础简介"""

from pydantic import BaseModel
from typing import Optional


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False  # 可选字段，默认为 False


def test(name: str = "World", price: float = 0.0, is_offer: bool = False) -> Item:
    return Item(name=name, price=price)
