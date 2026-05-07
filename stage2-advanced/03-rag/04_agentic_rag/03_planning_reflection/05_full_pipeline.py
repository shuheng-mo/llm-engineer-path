"""综合实战 — Planner + Executor + Reflector + Solver 全流程（含 Web 搜索 + Mock RAG）

对应课程章节：四 / 第三章 5.2

依赖:
uv pip install ddgs
"""
import operator
import os
import time
from typing import Annotated, List

from ddgs import DDGS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

llm = ChatOpenAI(
    model="qwen-plus",
    temperature=0,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)
print(">>> 模型初始化完成: Qwen-Plus")


# 2. Web 搜索工具
def web_search_tool(query: str, max_results: int = 5) -> str:
    print(f"    [Web] 正在搜索: {query} ...")
    with DDGS() as ddgs:
        results = [
            f"- {r.get('title', '')}\n  {r.get('body', '')}\n  {r.get('href', '')}"
            for r in ddgs.text(query, max_results=max_results)
        ]
    return "\n".join(results) if results else "未找到相关网页信息。"


# 3. 模拟 RAG 工具
def mock_retriever_tool(query: str):
    print(f"    [Tool] 正在检索: {query} ...")
    time.sleep(1)
    if "比亚迪" in query and "净利润" in query:
        return "【文档片段A】比亚迪2024年Q3财报显示，归母净利润为104.13亿元，同比增长8.2%。"
    if "特斯拉" in query and "净利润" in query:
        return "【文档片段B】特斯拉2024年Q3财报显示，GAAP净利润为21.67亿美元（约合人民币155亿元），同比增长17%。"
    if "情绪" in query or "风险" in query:
        return "【文档片段C】当前新能源车市场竞争加剧，分析师普遍认为价格战可能压缩利润空间，需警惕毛利率下降风险。"
    return "未找到相关具体数据，建议缩小搜索范围。"


# 4. State
class AgentState(TypedDict):
    objective: str
    plan: List[str]
    past_steps: Annotated[List[str], operator.add]
    scratchpad: str
    final_answer: str


# 5. Nodes
class PlanSchema(BaseModel):
    steps: List[str] = Field(description="解决问题所需的具体步骤列表，逻辑清晰")


planner_runner = llm.with_structured_output(PlanSchema)


def planner_node(state: AgentState):
    print(f"\n--- [1] Planner: 正在规划任务 '{state['objective']}' ---")
    prompt = f"""
    你是一个专家级任务规划器。请将目标拆解为简单的搜索或计算步骤。
    目标: {state['objective']}
    """
    plan_result = planner_runner.invoke(prompt)
    print(f"    -> 生成计划: {plan_result.steps}")
    return {"plan": plan_result.steps, "scratchpad": "Plan created."}


def executor_node(state: AgentState):
    plan = state["plan"]
    if not plan:
        return {"scratchpad": "No steps left."}

    current_step = plan[0]
    print(f"\n--- [2] Executor: 执行步骤 '{current_step}' ---")

    web_keywords = ["网页", "web", "最新", "新闻", "对比", "销量", "财报", "来源", "链接", "引用", "证据", "谁更强"]
    use_web = any(k in current_step.lower() for k in [kw.lower() for kw in web_keywords])

    if use_web:
        tool_name = "web_search_tool"
        tool_output = web_search_tool(current_step, max_results=5)
    else:
        tool_name = "mock_retriever_tool"
        tool_output = mock_retriever_tool(current_step)

    return {
        "past_steps": [f"工具: {tool_name}\n步骤: {current_step}\n结果: {tool_output}\n"],
        "plan": plan[1:],
        "scratchpad": "Step executed.",
    }


class ReflectionSchema(BaseModel):
    is_satisfactory: bool = Field(description="当前收集的信息是否足以回答用户问题")
    feedback: str = Field(description="如果不足，指出缺什么；如果足够，留空")
    next_step_suggestion: str = Field(description="如果不足，建议的一个补救步骤")


reflector_runner = llm.with_structured_output(ReflectionSchema)
MAX_REFLECTIONS = 5


def reflector_node(state: AgentState):
    print("\n--- [3] Reflector: 反思与评估 ---")
    if state.get("reflection_count", 0) >= MAX_REFLECTIONS:
        print("    -> 反思次数过多，跳过反思。")
        return {"scratchpad": "Reflection skipped due to max reflections"}

    context = "\n".join(state["past_steps"])
    prompt = f"""
    目标: {state['objective']}

    已获取的信息:
    {context}

    请判断信息是否充分？如果遇到"未找到数据"或信息矛盾，请标记为不满意。
    """
    reflection = reflector_runner.invoke(prompt)
    state["reflection_count"] = state.get("reflection_count", 0) + 1

    if reflection.is_satisfactory:
        print("    -> 评估通过：信息充足。")
        return {"scratchpad": "Reflection Passed"}

    print(f"    -> 评估未通过：{reflection.feedback}")
    new_plan = [reflection.next_step_suggestion] + state["plan"]
    return {"plan": new_plan, "scratchpad": f"Reflection Failed: {reflection.feedback}"}


def final_answer_node(state: AgentState):
    print("\n--- [4] Generator: 生成最终回答 ---")
    context = "\n".join(state["past_steps"])
    prompt = f"""
    基于以下检索到的信息，回答用户问题。确保数据准确，并进行适当的对比。

    信息:
    {context}

    问题: {state['objective']}
    """
    return {"final_answer": llm.invoke(prompt).content}


# 6. 构图
def router(state: AgentState):
    if state["scratchpad"].startswith("Reflection Failed"):
        return "executor"
    if len(state["plan"]) > 0:
        return "executor"
    return "final_answer"


workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("reflector", reflector_node)
workflow.add_node("final_answer", final_answer_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "reflector")
workflow.add_conditional_edges(
    "reflector", router, {"executor": "executor", "final_answer": "final_answer"}
)
workflow.add_edge("final_answer", END)

app = workflow.compile()


if __name__ == "__main__":
    question = "对比比亚迪和特斯拉2024年Q3的净利润，并结合市场情绪给出风险提示。"
    print(f"Start Processing Query: {question}")
    print("=" * 50)

    inputs = {"objective": question, "plan": [], "past_steps": [], "scratchpad": ""}
    result = app.invoke(inputs, config={"recursion_limit": 20})

    print("=" * 50)
    print("FINAL ANSWER:")
    print(result["final_answer"])
