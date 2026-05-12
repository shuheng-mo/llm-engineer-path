"""MMR 检索 — 在保证相关性的同时减少结果冗余

对应课程章节：一 / 6.x 扩展

问题：
    标准 similarity 检索找的是"和查询最像"的 Top-K 文档。但实际语料里常有大量近似
    文档（同一段话被切成多个相邻 chunk、不同来源的相似表述）。Top-K 全是近似复制，
    塞进 prompt 既浪费 token，也让 LLM 的回答缺乏多样性。

MMR (Maximal Marginal Relevance) 的核心思想：
    每选一篇文档时，不仅看它和 query 多相关，还要看它和【已选中的文档】有多不一样。
    数学表达（贪心算法，每步选一篇）：

        MMR_i = argmax_{D ∈ R \\ S} [ λ · sim(D, Q) - (1-λ) · max_{D' ∈ S} sim(D, D') ]

    符号含义：
        Q       — 查询
        R       — 候选池（向量库里 fetch_k 个最相关的）
        S       — 已经选出来的结果集合
        λ       — lambda_mult，0~1
            λ=1   → 纯相关性，等价于 similarity
            λ=0   → 纯多样性，最大化彼此差异
            λ=0.5 → 平衡（langchain 默认值）

工程参数：
    fetch_k    — 候选池大小（多召回一些，再让 MMR 挑出多样的 k 个）
    lambda_mult — 上面的 λ
    k          — 最终返回数量

依赖：rag group 已经装了 langchain-chroma + dashscope embeddings。
"""

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

load_dotenv()


# ============================================================
# 1. 故意构造冗余语料 —— 让 similarity 和 MMR 的差别能看出来
# ============================================================
# 主题分三组：
# - LangChain 介绍（4 条几乎重复）
# - RAG 工作原理（2 条相似）
# - 别的话题（向量库、Agent 概念）
documents = [
    Document(page_content="LangChain 是一个用于开发大模型应用的开源框架。"),
    Document(page_content="LangChain 是开源的 LLM 应用开发框架。"),
    Document(page_content="LangChain 是一个开源框架，用于构建基于 LLM 的应用。"),
    Document(page_content="LangChain 提供了一套工具和抽象，帮助开发者基于大语言模型快速构建应用。"),
    Document(page_content="RAG 通过先检索相关文档再让 LLM 生成答案，缓解了模型的幻觉问题。"),
    Document(
        page_content="检索增强生成（RAG）的工作流程是：先从知识库检索相关内容，再交给模型生成回答。"
    ),
    Document(page_content="向量数据库存储文档的 embedding，支持基于相似度的快速近邻检索。"),
    Document(page_content="Agent 是被赋予工具调用能力的 LLM，可以自主决策调用哪个工具来完成任务。"),
]


embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)


def show(title: str, docs: list[Document]):
    print(f"\n{title}")
    print("-" * 60)
    for i, doc in enumerate(docs, 1):
        print(f"  {i}. {doc.page_content}")


query = "LangChain 是什么？"
print(f"查询: {query}")


# ============================================================
# 2. similarity vs MMR：直接对比 Top-3 结果
# ============================================================
sim_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

mmr_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 8,  # 先从向量库取 8 个候选，再 MMR 挑 3 个
        "lambda_mult": 0.5,  # 一半相关性、一半多样性
    },
)

# 预期：
#   similarity → Top-3 全是 LangChain 介绍（重复）
#   MMR        → 1 条 LangChain + 1 条 RAG + 1 条更远主题
show("[A] similarity（纯相关性）", sim_retriever.invoke(query))
show("[B] MMR (lambda_mult=0.5, fetch_k=8)", mmr_retriever.invoke(query))


# ============================================================
# 3. lambda_mult 的影响 —— 同样的 MMR，调旋钮看变化
# ============================================================
print("\n\n=== lambda_mult 的极端值对比 ===")

for lam in [1.0, 0.5, 0.0]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 8, "lambda_mult": lam},
    )
    label = {1.0: "纯相关 (退化为 similarity)", 0.5: "平衡", 0.0: "纯多样性"}[lam]
    show(f"[lambda_mult={lam}] {label}", retriever.invoke(query))


# ============================================================
# 4. fetch_k 的影响 —— 候选池越大，多样性空间越大
# ============================================================
print("\n\n=== fetch_k 的影响（lambda_mult=0.5 固定）===")

for fk in [3, 5, len(documents)]:
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": fk, "lambda_mult": 0.5},
    )
    show(f"[fetch_k={fk}]", retriever.invoke(query))

# 经验值：
#   fetch_k = k         → 没空间挑，MMR 退化（候选 = 结果）
#   fetch_k = 3*k ~ 5*k → 工业界常用区间，能体现多样性又不至于召回噪声太多
#   fetch_k = ∞         → 召回过多噪声，MMR 反而可能选出弱相关文档
