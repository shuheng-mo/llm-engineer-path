"""DocString 最佳实践 — DocString 是 LLM 理解工具用途的唯一依据

对应课程章节：模块三 / 1.1.3
"""
from langchain.tools import tool


@tool
def search_product(
    keyword: str,
    category: str = "all",
    max_price: float | None = None,
    min_rating: float = 4.0,
) -> str:
    """在电商平台搜索商品。

    使用场景：
    - 用户想要查找特定商品时调用
    - 用户询问"有什么XX产品"、"帮我找XX"时使用

    Args:
        keyword: 搜索关键词，例如"手机"、"笔记本电脑"
        category: 商品分类，可选值："electronics"(电子产品)、"clothing"(服装)、"all"(全部)
        max_price: 最高价格限制，单位为元，不设置则不限制
        min_rating: 最低评分要求，范围 1.0-5.0，默认 4.0

    Returns:
        JSON 格式的商品列表，包含名称、价格、评分等信息

    注意事项：
    - 关键词尽量具体，避免过于宽泛
    - 价格限制时请考虑用户预算
    - 评分过滤会影响结果数量
    """
    return "TODO: 实际实现"
