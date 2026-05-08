"""并行执行（Fan-out / Fan-in） — Send + Annotated[list, add] 自动合并

对应课程章节：模块二 / 4.1
"""
import os
from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

load_dotenv()

llm = ChatTongyi(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
)


class State(TypedDict):
    query: str
    # results 用 Annotated[list, add] —— 三个并行节点返回的 list 会被自动拼接而不是覆盖
    results: Annotated[list[str], add]
    final_answer: str


def search_web(state: State) -> dict:
    return {"results": [f"Web 结果: {state['query']}"]}


def search_kb(state: State) -> dict:
    return {"results": [f"知识库结果: {state['query']}"]}


def search_db(state: State) -> dict:
    return {"results": [f"数据库结果: {state['query']}"]}


def aggregate(state: State) -> dict:
    combined = "\n".join(state["results"])
    answer = llm.invoke(f"综合以下信息回答：\n{combined}")
    return {"final_answer": answer.content}


def fan_out(state: State):
    """从 START 同时分发到三个搜索节点。"""
    return [
        Send("search_web", state),
        Send("search_kb", state),
        Send("search_db", state),
    ]


builder = StateGraph(State)
builder.add_node("search_web", search_web)
builder.add_node("search_kb", search_kb)
builder.add_node("search_db", search_db)
builder.add_node("aggregate", aggregate)

builder.add_conditional_edges(START, fan_out)   # 扇出
builder.add_edge("search_web", "aggregate")     # 扇入
builder.add_edge("search_kb", "aggregate")
builder.add_edge("search_db", "aggregate")
builder.add_edge("aggregate", END)

graph = builder.compile()

if __name__ == "__main__":
    print(graph.invoke({"query": "如何使用 LangGraph?"}))
