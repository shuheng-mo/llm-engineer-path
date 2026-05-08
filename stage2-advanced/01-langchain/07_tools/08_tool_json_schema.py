"""查看工具自动生成的 JSON Schema

对应课程章节：第八章 / 4.2
"""
import json

from langchain_core.tools import tool


@tool
def search_products(
    query: str,
    category: str = "all",
    max_price: float = None,
) -> str:
    """搜索商品。

    Args:
        query: 搜索关键词
        category: 商品类别，默认搜索全部
        max_price: 最高价格限制（可选）

    Returns:
        搜索结果列表
    """
    return f"搜索 {query} 在 {category} 类别，价格上限 {max_price}"


print(json.dumps(search_products.args_schema.model_json_schema(), indent=2, ensure_ascii=False))
