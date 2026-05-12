"""用 LangGraph 编排上面 4 个节点 — Corrective RAG 闭环

对应课程章节：四 / 第四章 5
"""

from langgraph.graph import END, StateGraph

# 假设已导入 GraphState 和上面 4 个节点
# from .02_graph_state import GraphState
# from .03_retrieve_node import retrieve ...

workflow = StateGraph(GraphState)  # noqa: F821

workflow.add_node("retrieve", retrieve)  # noqa: F821
workflow.add_node("grade_documents", grade_documents)  # noqa: F821
workflow.add_node("generate", generate)  # noqa: F821
workflow.add_node("rewrite", rewrite)  # noqa: F821

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")


def decide_to_generate(state):
    """没相关文档就重写查询，有就去生成。"""
    if not state["documents"]:
        print("---DECISION: 所有文档均无关，转去重写---")
        return "rewrite"
    print("---DECISION: 文档质量达标，转去生成---")
    return "generate"


workflow.add_conditional_edges(
    "grade_documents", decide_to_generate, {"rewrite": "rewrite", "generate": "generate"}
)

workflow.add_edge("rewrite", "retrieve")  # 闭环：重写后再检索
workflow.add_edge("generate", END)

app = workflow.compile()
