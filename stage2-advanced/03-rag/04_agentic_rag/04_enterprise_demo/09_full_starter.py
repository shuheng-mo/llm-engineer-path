"""企业级 Agentic RAG — 完整实战代码（Planner + Corrective RAG SubGraph）

对应课程章节：四 / 第四章 8
"""

import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# =============================================================================
# 0) 环境与模型
# =============================================================================
load_dotenv()
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")

if not os.environ.get("DASHSCOPE_API_KEY"):
    print("⚠️ 警告: 未检测到 DASHSCOPE_API_KEY，请确保环境变量已设置。")

llm = ChatTongyi(model="qwen-max", temperature=0)


# =============================================================================
# 1) 从 MD 文档构建向量库
# =============================================================================
def build_vectorstore_from_md(
    md_dir: str,
    embedding_model: str = "text-embedding-v1",
    persist_dir: Optional[str] = None,
):
    loader = DirectoryLoader(
        md_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=True,
    )
    raw_docs = loader.load()
    if not raw_docs:
        raise ValueError(f"未在目录 {md_dir} 找到任何 .md 文件")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    docs = splitter.split_documents(raw_docs)

    embeddings = DashScopeEmbeddings(model=embedding_model)
    if persist_dir:
        return Chroma.from_documents(
            documents=docs, embedding=embeddings, persist_directory=persist_dir
        )
    return Chroma.from_documents(documents=docs, embedding=embeddings)


print("--- [系统启动] 正在初始化向量数据库（从MD加载）---")
vectorstore = build_vectorstore_from_md(
    md_dir=str(DATA_DIR), persist_dir=str(DATA_DIR / "chroma_db")
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
print("--- [系统启动] 向量数据库准备完毕 ---")


# =============================================================================
# Part A: SubGraph - Corrective RAG Worker
# =============================================================================
class SubGraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    search_count: int


def format_docs(docs: List[Document]) -> str:
    if not docs:
        return ""
    blocks = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "unknown")
        blocks.append(f"[Doc {i} | source={src}]\n{d.page_content}")
    return "\n\n".join(blocks)


def retrieve_node(state: SubGraphState):
    print(f"  [Worker] 正在检索: {state['question']}")
    return {"documents": retriever.invoke(state["question"])}


def grade_documents_node(state: SubGraphState):
    print("  [Worker] 正在评估文档质量...")
    question = state["question"]
    documents = state.get("documents", [])

    class Grade(BaseModel):
        binary_score: str = Field(description="相关则 'yes'，否则 'no'")

    grader_llm = llm.with_structured_output(Grade)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是严格的检索结果评估器。只判断：文档是否包含回答问题所需的关键信息。相关=yes，不相关=no。",
            ),
            ("human", "问题:\n{question}\n\n文档:\n{document}"),
        ]
    )
    grade_chain = prompt | grader_llm

    filtered = []
    for doc in documents:
        res = grade_chain.invoke({"question": question, "document": doc.page_content})
        if (res.binary_score or "").strip().lower() == "yes":
            filtered.append(doc)
    return {"documents": filtered}


def rewrite_node(state: SubGraphState):
    print("  [Worker] ⚠️ 文档无关，正在重写查询...")
    question = state["question"]
    msg = HumanMessage(
        content=(
            "请将下面问题改写为更适合向量检索的中文查询语句。\n"
            "要求：\n"
            "1) 必须保持原问题语义不变（年份、公司、指标等关键实体必须保留）\n"
            "2) 更偏“名词短语/关键词组合”，避免长句\n"
            "3) 只输出改写后的查询语句，不要解释\n\n"
            f"原问题：{question}"
        )
    )
    better_question = llm.invoke([msg]).content.strip()
    count = state.get("search_count", 0) + 1
    print(f"  [Worker] 新查询: {better_question} (search_count={count})")
    return {"question": better_question, "search_count": count}


def generate_node(state: SubGraphState):
    print("  [Worker] 正在生成单步答案...")
    question = state["question"]
    docs = state.get("documents", [])
    context = format_docs(docs)

    prompt = ChatPromptTemplate.from_template(
        "你是金融分析助手。请严格基于已知信息回答。\n"
        "若已知信息不足以回答，直接说“未在资料中找到相关信息”。\n\n"
        "已知信息:\n{context}\n\n"
        "问题: {question}\n"
        "回答:"
    )
    chain = prompt | llm | StrOutputParser()
    return {"generation": chain.invoke({"context": context, "question": question})}


def decide_next_step(state: SubGraphState):
    docs = state.get("documents", [])
    count = state.get("search_count", 0)
    if not docs:
        if count >= 2:
            print("  [Worker] 重试次数过多，停止重写，直接生成兜底回答")
            return "generate"
        return "rewrite"
    return "generate"


sub_workflow = StateGraph(SubGraphState)
sub_workflow.add_node("retrieve", retrieve_node)
sub_workflow.add_node("grade", grade_documents_node)
sub_workflow.add_node("rewrite", rewrite_node)
sub_workflow.add_node("generate", generate_node)

sub_workflow.set_entry_point("retrieve")
sub_workflow.add_edge("retrieve", "grade")
sub_workflow.add_conditional_edges(
    "grade", decide_next_step, {"rewrite": "rewrite", "generate": "generate"}
)
sub_workflow.add_edge("rewrite", "retrieve")
sub_workflow.add_edge("generate", END)

rag_worker = sub_workflow.compile()


# =============================================================================
# Part B: Main Graph - Planner
# =============================================================================
class Plan(BaseModel):
    steps: List[str] = Field(description="可检索的事实型子问题列表")


class MainState(TypedDict):
    input: str
    plan: List[str]
    past_steps: List[Tuple[str, str]]
    final_answer: str


def planner_node(state: MainState):
    print("\n--- [Planner] 正在规划任务 ---")
    question = state["input"]

    planner_llm = llm.with_structured_output(Plan)
    system_prompt = (
        "你是专业的金融分析师助理。\n"
        "请把用户复杂问题拆成若干【可检索的事实型子问题】（每一步都应该能通过资料检索得到明确答案）。\n"
        "强约束：\n"
        "1) 每一步必须包含关键实体（公司/年份/指标，如研发投入、毛利率等）\n"
        "2) 避免“分析一下/写报告/给建议”等不可检索表述\n"
        "3) 步骤数量 2~5 个\n"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )
    plan_obj = (prompt | planner_llm).invoke({"question": question})
    steps = [s.strip() for s in plan_obj.steps if s.strip()]
    print(f"--- [Planner] 生成计划: {steps} ---")
    return {"plan": steps, "past_steps": []}


def executor_node(state: MainState):
    plan = state["plan"]
    current_step = plan[0]
    print(f"\n--- [Executor] 执行步骤: {current_step} ---")

    worker_output = rag_worker.invoke(
        {
            "question": current_step,
            "search_count": 0,
            "documents": [],
            "generation": "",
        }
    )

    step_result = worker_output.get("generation", "")
    print(f"--- [Executor] 步骤结果: {step_result} ---")

    return {
        "past_steps": state["past_steps"] + [(current_step, step_result)],
        "plan": plan[1:],
    }


def solver_node(state: MainState):
    print("\n--- [Solver] 汇总最终答案 ---")
    original_question = state["input"]
    past_steps = state["past_steps"]
    context_str = "\n\n".join(f"步骤: {step}\n结果: {res}" for step, res in past_steps)

    prompt = ChatPromptTemplate.from_template(
        "你是严谨的金融分析师。\n"
        "请根据分步研究结果，回答用户原始问题，要求：\n"
        "1) 给出 2022 vs 2023 的数据对比（研发投入、毛利率）\n"
        "2) 解释变化原因（若资料不足要明确说明）\n"
        "3) 行文结构清晰：结论 -> 数据 -> 原因\n\n"
        "用户问题: {question}\n\n"
        "研究过程:\n{context}\n\n"
        "最终回答:"
    )
    chain = prompt | llm | StrOutputParser()
    return {"final_answer": chain.invoke({"question": original_question, "context": context_str})}


def should_continue(state: MainState):
    return "continue" if state["plan"] else "end"


workflow = StateGraph(MainState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("solver", solver_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_conditional_edges(
    "executor", should_continue, {"continue": "executor", "end": "solver"}
)
workflow.add_edge("solver", END)

app = workflow.compile()


# =============================================================================
# Part C: 运行
# =============================================================================
if __name__ == "__main__":
    user_query = "请分析特斯拉2023年相比2022年，研发投入的变化以及毛利率的变化，并简述原因。"
    print("=" * 50)
    print(f"用户提问: {user_query}")
    print("=" * 50)

    final_state = app.invoke({"input": user_query}, config={"recursion_limit": 50})

    print("\n" + "=" * 50)
    print("最终分析报告:\n")
    print(final_state["final_answer"])
