"""ToolNode + tools_condition — 自动构建 ReAct 风格 Agent

对应课程章节：模块三 / 2.2.2
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天，25°C"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [get_weather, get_time]

model = ChatTongyi(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
).bind_tools(tools)


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))  # 自动并行处理工具调用

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [{"role": "user", "content": "北京和上海的天气？"}]})
    for msg in result["messages"]:
        print(f"[{msg.type}]: {msg.content}")
