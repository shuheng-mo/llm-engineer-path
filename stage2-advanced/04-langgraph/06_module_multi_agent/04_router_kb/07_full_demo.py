"""Router — 完整 demo：端到端可运行的多源知识库路由器

把 01~06 各步骤串成一个可独立运行的脚本：

  Step 1  RouterState / Classification / AgentInput / AgentOutput  (对应 01_state.py)
  Step 2  6 个搜索工具（github / notion / slack 各 2）              (对应 02_tools.py)
  Step 3  3 个垂直专家 Agent                                         (对应 03_specialist_agents.py)
  Step 4  分类器 + Send 路由 + 节点 + 综合器                         (对应 04_classifier_routing.py)
  Step 5  用链式 API 编译 StateGraph                                 (对应 05_compile_workflow.py)
  Step 6  跑示例 query 验证多源并行 + 综合                            (对应 06_run_demo.py)

核心 idea —— "Map-Reduce 风格的多源路由"：
  Classifier (Map) → Send 并行分发到 N 个专家 → results 用 operator.add 累加
  → Synthesizer (Reduce) 汇总成最终答案

运行：
    uv run python stage2-advanced/04-langgraph/06_module_multi_agent/04_router_kb/07_full_demo.py
    uv run python .../07_full_demo.py --query "如何认证API请求？"
"""

import operator
import pathlib
import sys
from typing import Annotated, Literal, TypedDict

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402


# ============================================================
# Step 1：状态
# ============================================================
class AgentInput(TypedDict):
    query: str


class AgentOutput(TypedDict):
    source: str
    result: str


class Classification(TypedDict):
    source: Literal["github", "notion", "slack"]
    query: str


class RouterState(TypedDict):
    query: str
    classifications: list[Classification]
    # operator.add 让多个并行节点的 results 列表自动合并
    results: Annotated[list[AgentOutput], operator.add]
    final_answer: str


# ============================================================
# Step 2：各垂直领域工具
# ============================================================
@tool
def search_code(query: str) -> str:
    """在 GitHub 仓库中搜索代码。"""
    return f"在代码库找到匹配 '{query}' 的结果：src/auth.py 中的认证中间件"


@tool
def search_issues(query: str) -> str:
    """搜索 GitHub 问题和 PR。"""
    return f"找到 3 个匹配 '{query}' 的 issue：#142, #89, #203"


@tool
def search_notion(query: str) -> str:
    """在 Notion 工作空间搜索文档。"""
    return "找到文档：'API 认证指南' - 涵盖 OAuth2 流程和 JWT 令牌"


@tool
def get_page(page_id: str) -> str:
    """获取特定 Notion 页面。"""
    return "页面内容：认证设置的分步说明"


@tool
def search_slack(query: str) -> str:
    """搜索 Slack 消息和线程。"""
    return "在 #engineering 发现讨论：'使用 Bearer 令牌进行 API 认证'"


@tool
def get_thread(thread_id: str) -> str:
    """获取特定 Slack 线程。"""
    return "线程讨论了 API 密钥轮换的最佳实践"


# ============================================================
# Step 3：三个专业 Agent
# ============================================================
model = get_chat_model("qwen-max")

github_agent = create_agent(
    model,
    tools=[search_code, search_issues],
    system_prompt="你是 GitHub 专家。搜索代码、issue 和 PR 回答问题。",
)

notion_agent = create_agent(
    model,
    tools=[search_notion, get_page],
    system_prompt="你是 Notion 专家。搜索文档回答问题。",
)

slack_agent = create_agent(
    model,
    tools=[search_slack, get_thread],
    system_prompt="你是 Slack 专家。搜索讨论回答问题。",
)


# ============================================================
# Step 4：分类器 + Send 路由 + 节点 + 综合器
# ============================================================
class ClassificationResult(BaseModel):
    """LLM 结构化输出的 schema。"""

    classifications: list[Classification] = Field(description="要调用的 Agent 列表及其针对性子问题")


def classify_query(state: RouterState) -> dict:
    """让 LLM 把原始 query 拆成"调哪些 source / 各 source 问什么子问题"。"""
    structured_llm = model.with_structured_output(ClassificationResult)
    result = structured_llm.invoke(
        [
            {
                "role": "system",
                "content": (
                    "分析查询并确定要咨询哪些知识库。\n\n"
                    "可用来源：\n"
                    "- github: 代码、API 参考、实现细节\n"
                    "- notion: 内部文档、流程、策略\n"
                    "- slack: 团队讨论、非正式知识\n\n"
                    "仅返回与查询相关的来源。"
                ),
            },
            {"role": "user", "content": state["query"]},
        ]
    )
    # with_structured_output 返回的是 pydantic model；ruff 不会推断，cast 一下取属性即可
    classifications = result.classifications  # type: ignore[union-attr]
    return {"classifications": classifications}


def route_to_agents(state: RouterState) -> list[Send]:
    """用 Send 并行分发：每个分类发到对应 source 节点。

    Send 比 add_conditional_edges 的字符串返回值更强：能给每个目标节点带
    各自的子 state（这里是 {"query": c["query"]}）。
    """
    return [Send(c["source"], {"query": c["query"]}) for c in state["classifications"]]


def query_github(state: AgentInput) -> dict:
    result = github_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"results": [{"source": "github", "result": result["messages"][-1].content}]}


def query_notion(state: AgentInput) -> dict:
    result = notion_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"results": [{"source": "notion", "result": result["messages"][-1].content}]}


def query_slack(state: AgentInput) -> dict:
    result = slack_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"results": [{"source": "slack", "result": result["messages"][-1].content}]}


def synthesize_results(state: RouterState) -> dict:
    """把各专家的回答合并成一个最终回复。"""
    if not state["results"]:
        return {"final_answer": "未从任何知识源找到结果。"}

    formatted = [f"**来自 {r['source'].title()}：**\n{r['result']}" for r in state["results"]]
    response = model.invoke(
        [
            {
                "role": "system",
                "content": (
                    f'综合搜索结果回答："{state["query"]}"\n' "合并信息，避免冗余，保持简洁。"
                ),
            },
            {"role": "user", "content": "\n\n".join(formatted)},
        ]
    )
    return {"final_answer": response.content}


# ============================================================
# Step 5：编译工作流
# ============================================================
workflow = (
    StateGraph(RouterState)
    .add_node("classify", classify_query)
    .add_node("github", query_github)
    .add_node("notion", query_notion)
    .add_node("slack", query_slack)
    .add_node("synthesize", synthesize_results)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)


# ============================================================
# Step 6：跑示例
# ============================================================
def run_demo(query: str) -> None:
    print(f"\n========== Query ==========\n{query}\n")
    result = workflow.invoke({"query": query})

    print("---------- 分类（classifier 决定调哪些 source） ----------")
    for c in result["classifications"]:
        print(f"  · {c['source']:<7} → {c['query']}")

    print("\n---------- 各专家结果（并行执行后汇总） ----------")
    for r in result["results"]:
        print(f"\n[{r['source']}]")
        print(r["result"])

    print("\n---------- 综合答案 ----------")
    print(result["final_answer"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Router 多源知识库端到端 demo")
    parser.add_argument(
        "--query",
        default="如何认证 API 请求？",
        help="要问的问题（默认演示一个 3 源并触发的问题）",
    )
    args = parser.parse_args()
    run_demo(args.query)
