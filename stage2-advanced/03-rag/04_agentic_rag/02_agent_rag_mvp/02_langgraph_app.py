"""Agent + RAG MVP — 用 StateGraph + ToolNode 拼装

对应课程章节：四 / 第二章 2.5.3
"""

from typing import Literal

from langchain_community.chat_models import ChatTongyi
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

# from .01_rag_tool import tools   # 实际项目里可以这样 import
tools = []  # placeholder — 把 01_rag_tool.py 里 tools 复制过来或 import


# 1. 初始化 Qwen 并 bind 工具
llm = ChatTongyi(model="qwen-plus")
llm_with_tools = llm.bind_tools(tools)


# 2. Agent 节点
def agent_node(state: MessagesState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# 工具节点
tool_node = ToolNode(tools)


# 3. 条件边
def should_continue(state: MessagesState) -> Literal["tools", END]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# 4. 构建图
workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")  # 工具结果回流给 Agent

app = workflow.compile()
