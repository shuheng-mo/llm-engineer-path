"""Router — Step 4：分类器 + Send 路由 + 各 Agent 节点 + 综合器

对应课程章节：模块六 / 五 / Step 4
"""
from langgraph.types import Send
from pydantic import BaseModel, Field

# from .01_state import Classification, RouterState, AgentInput
# from .03_specialist_agents import github_agent, notion_agent, slack_agent, model


# 4.1 分类器
class ClassificationResult(BaseModel):
    classifications: list["Classification"] = Field(                # noqa: F821
        description="要调用的Agent列表及其针对性子问题"
    )


def classify_query(state: "RouterState") -> dict:                   # noqa: F821
    structured_llm = model.with_structured_output(ClassificationResult)   # noqa: F821

    result = structured_llm.invoke([
        {
            "role": "system",
            "content": """分析查询并确定要咨询哪些知识库。

                可用来源：
                - github: 代码、API参考、实现细节
                - notion: 内部文档、流程、策略
                - slack: 团队讨论、非正式知识

                仅返回与查询相关的来源。
            """,
        },
        {"role": "user", "content": state["query"]},
    ])

    return {"classifications": result.classifications}


# 4.2 路由函数（用 Send 并行分发到多个专家）
def route_to_agents(state: "RouterState") -> list[Send]:            # noqa: F821
    return [
        Send(c["source"], {"query": c["query"]})
        for c in state["classifications"]
    ]


# 4.3 Agent 节点
def query_github(state: "AgentInput") -> dict:                      # noqa: F821
    result = github_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})  # noqa: F821
    return {"results": [{"source": "github", "result": result["messages"][-1].content}]}


def query_notion(state: "AgentInput") -> dict:                      # noqa: F821
    result = notion_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})  # noqa: F821
    return {"results": [{"source": "notion", "result": result["messages"][-1].content}]}


def query_slack(state: "AgentInput") -> dict:                       # noqa: F821
    result = slack_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})   # noqa: F821
    return {"results": [{"source": "slack", "result": result["messages"][-1].content}]}


# 4.4 综合器
def synthesize_results(state: "RouterState") -> dict:               # noqa: F821
    if not state["results"]:
        return {"final_answer": "未从任何知识源找到结果。"}

    formatted = [
        f"**来自 {r['source'].title()}：**\n{r['result']}"
        for r in state["results"]
    ]

    response = model.invoke([                                       # noqa: F821
        {
            "role": "system",
            "content": f"""综合搜索结果回答："{state['query']}"
合并信息，避免冗余，保持简洁。""",
        },
        {"role": "user", "content": "\n\n".join(formatted)},
    ])

    return {"final_answer": response.content}
