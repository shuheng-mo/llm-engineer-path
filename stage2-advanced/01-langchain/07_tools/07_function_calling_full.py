"""完整 Function Calling 流程 — 双轮调用：LLM → tool exec → LLM 整合

对应课程章节：第八章 / 3.2.2
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)


@tool
def get_stock_price(symbol: str) -> str:
    """查询股票价格。"""
    prices = {"AAPL": "178.50 USD", "GOOGL": "141.20 USD", "MSFT": "378.90 USD"}
    return prices.get(symbol.upper(), f"未找到 {symbol} 的价格")


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """货币转换。"""
    rates = {("USD", "CNY"): 7.24, ("CNY", "USD"): 0.138, ("USD", "EUR"): 0.92}
    rate = rates.get((from_currency.upper(), to_currency.upper()), None)
    if rate:
        return f"{amount} {from_currency} = {amount * rate:.2f} {to_currency}"
    return f"不支持 {from_currency} 到 {to_currency} 的转换"


tools = [get_stock_price, convert_currency]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def chat_with_tools(query: str):
    """支持工具调用的对话函数"""
    messages = [HumanMessage(content=query)]

    # 第一次调用：让模型决定是否需要工具
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        return response.content

    # 执行所有工具调用
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        print(f"[调用工具] {tool_name}({tool_args})")
        result = (
            tool_map[tool_name].invoke(tool_args)
            if tool_name in tool_map
            else f"未知工具: {tool_name}"
        )
        print(f"[工具结果] {result}")

        messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    # 第二次调用：让模型整合工具结果
    final_response = llm_with_tools.invoke(messages)
    return final_response.content


if __name__ == "__main__":
    print("测试 1: 股票查询")
    print(chat_with_tools("苹果公司的股票现在多少钱？"))

    print("\n" + "=" * 50)
    print("测试 2: 货币转换")
    print(chat_with_tools("帮我把 100 美元换算成人民币"))
