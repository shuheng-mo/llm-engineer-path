"""Router — Step 5：用链式 API 编译工作流

对应课程章节：模块六 / 五 / Step 5
"""
from langgraph.graph import END, START, StateGraph

# from .01_state import RouterState
# from .04_classifier_routing import (
#     classify_query, query_github, query_notion, query_slack,
#     route_to_agents, synthesize_results,
# )

workflow = (
    StateGraph(RouterState)                                         # noqa: F821
    .add_node("classify", classify_query)                           # noqa: F821
    .add_node("github", query_github)                               # noqa: F821
    .add_node("notion", query_notion)                               # noqa: F821
    .add_node("slack", query_slack)                                 # noqa: F821
    .add_node("synthesize", synthesize_results)                     # noqa: F821
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])  # noqa: F821
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)
