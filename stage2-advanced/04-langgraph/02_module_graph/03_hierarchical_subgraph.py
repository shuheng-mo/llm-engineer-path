"""分层结构 — 把子图当作主图的一个节点（同名字段自动传递）

对应课程章节：模块二 / 4.3
"""

import pathlib
import sys
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

llm = get_chat_model("qwen-max", temperature=0.7)


# ============ 子图：深度研究 ============
class ResearchState(TypedDict):
    topic: str
    search_results: list[str]
    summary: str


def search_node(state: ResearchState) -> dict:
    return {"search_results": [f"搜索结果: {state['topic']}"]}


def summarize_node(state: ResearchState) -> dict:
    return {"summary": f"总结: {state['search_results']}"}


research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search_node)
research_builder.add_node("summarize", summarize_node)
research_builder.add_edge(START, "search")
research_builder.add_edge("search", "summarize")
research_builder.add_edge("summarize", END)
research_subgraph = research_builder.compile()


# ============ 主图 ============
class MainState(TypedDict):
    topic: str  # 与子图同名，自动传递
    summary: str  # 与子图同名，自动回传
    final_report: str


def generate_report(state: MainState) -> dict:
    report = llm.invoke(f"根据以下总结生成报告：\n{state['summary']}")
    return {"final_report": report.content}


main_builder = StateGraph(MainState)
main_builder.add_node("research", research_subgraph)  # 子图直接当节点
main_builder.add_node("report", generate_report)
main_builder.add_edge(START, "research")
main_builder.add_edge("research", "report")
main_builder.add_edge("report", END)

main_graph = main_builder.compile()

if __name__ == "__main__":
    print(main_graph.invoke({"topic": "如何使用 LangGraph?"}))
