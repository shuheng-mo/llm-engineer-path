"""处理多个工具调用 — 一次 AIMessage 中并发触发多个 tool_calls

对应课程章节：第八章 / 4.3
"""

import os
from datetime import datetime

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
def get_weather(city: str) -> str:
    """获取城市天气"""
    return {"北京": "晴 25°C", "上海": "多云 28°C"}.get(city, "未知")


@tool
def get_time(timezone: str) -> str:
    """获取指定时区的时间"""
    return datetime.now().strftime("%H:%M:%S")


tools = [get_weather, get_time]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def process_multi_tool_query(query: str):
    messages = [HumanMessage(content=query)]
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        return response.content

    print(f"[需要调用 {len(response.tool_calls)} 个工具]")
    for tc in response.tool_calls:
        name, args, tid = tc["name"], tc["args"], tc["id"]
        print(f"  - {name}({args})")
        result = tool_map[name].invoke(args) if name in tool_map else "未知工具"
        messages.append(ToolMessage(content=str(result), tool_call_id=tid))

    return llm_with_tools.invoke(messages).content


print(process_multi_tool_query("北京的天气怎么样？现在几点了？"))
