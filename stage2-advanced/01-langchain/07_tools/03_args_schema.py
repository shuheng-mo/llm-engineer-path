"""用 Pydantic args_schema 定义工具参数

对应课程章节：第八章 / 2.2.2
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """计算器工具的输入参数"""

    expression: str = Field(description="要计算的数学表达式，如 '2 + 3 * 4'")


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """安全地计算数学表达式并返回结果。

    支持基本的加减乘除运算。
    """
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"
