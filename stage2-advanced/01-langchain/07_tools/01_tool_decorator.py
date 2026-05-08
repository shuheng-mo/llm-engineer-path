"""@tool 装饰器最基础用法 — 自动从 type hints + docstring 推 schema

对应课程章节：第八章 / 2.1.1
"""
from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """将两个整数相加并返回结果。

    Args:
        a: 第一个整数
        b: 第二个整数

    Returns:
        两个整数的和
    """
    return a + b


print(f"工具名称: {add.name}")
print(f"工具描述: {add.description}")
print(f"参数 Schema: {add.args_schema.model_json_schema()}")
