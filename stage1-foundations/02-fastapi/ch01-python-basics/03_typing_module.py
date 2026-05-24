"""1.1 typing 模块写法 (Optional/List/Dict/Union)"""

from typing import Optional, List, Dict, Union


# 定义一个处理分数的函数
def process_scores(scores: List[int]) -> Dict[str, float]:
    return {"average": sum(scores) / len(scores)}


# 定义一个允许缺省的搜索函数
def search_item(query: Optional[str] = None) -> Union[str, List[str]]:  # 返回字符串或者字符串列表
    if query:
        return f"Searching for {query}"
    return ["item1", "item2"]
