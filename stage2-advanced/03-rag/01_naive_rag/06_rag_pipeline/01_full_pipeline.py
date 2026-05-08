"""RAG Pipeline 端到端完整示例（loader → splitter → vectorstore → mmr retriever → chain → CLI）

对应课程章节：一 / 7.x

本文件目标：用最少的代码量串起一个**可运行的 Naive RAG**，并在每一步注释清楚
"为什么这样写"。读完这一页，你应该能独立把任何文档变成可以问答的知识库。

整体数据流：

    用户问题
       │
       ├──→ Retriever ──→ Top-k Documents ──→ format_docs() ──→ 字符串 context
       │                                                            │
       │                                                            ▼
       └──────────────────────────────────────────────→ ChatPromptTemplate
                                                                    │
                                                                    ▼
                                                                  LLM
                                                                    │
                                                                    ▼
                                                          StrOutputParser → 答案
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
load_dotenv()


# ============================================================
# Step 1：模型 & Embedding 初始化
# ============================================================
# 注意 LLM 和 Embedding 是两个完全独立的模型：
#   - LLM 负责"理解 + 生成" → 回答问题
#   - Embedding 负责"把文本变成向量" → 让向量库能算相似度
# RAG 场景下 temperature 建议 0.2-0.4：太低会过于死板复读资料，太高容易脱离资料编造。
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)


# ============================================================
# Step 2：文档加载 + 切分
# ============================================================
# Loader 把异构文件统一成 List[Document]（page_content + metadata 两个字段）。
# 后续所有组件都吃 Document，所以加载阶段是统一接口的入口。
loader = PyPDFLoader(str(DATA_DIR / "LangChain.pdf"))
documents = loader.load()

# 为什么必须切分？三个理由：
#   1. Embedding 模型有最大输入长度（通常 512-8192 tokens），整文档一次塞不下。
#   2. 太大的 chunk 检索时"语义稀释" —— 一段含 5 个主题，向量是 5 个的平均，
#      跟具体问题的相似度反而下降。
#   3. LLM 上下文窗口有限，把无关内容塞进 prompt 是浪费 token 也增加幻觉风险。
#
# RecursiveCharacterTextSplitter 的 separators 是按优先级递归尝试：
# 优先按 \n\n（段落）切，切不下来再 \n（行），再 。/. （句子），最后字符级。
# 这样能尽量保留语义边界。
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,         # 每 chunk 的最大字符数（不是 tokens！）
    chunk_overlap=50,       # 相邻 chunk 重叠 50 字 → 避免边界处的句子被切断造成语义丢失
    separators=["\n\n", "\n", "。", ".", " ", ""],
)
chunks = splitter.split_documents(documents)


# ============================================================
# Step 3：向量化存储
# ============================================================
# from_documents 内部做的事：
#   1. 对每个 chunk 调用 embeddings.embed_documents() 转成向量
#   2. 把 (向量, page_content, metadata) 三元组写入 Chroma collection
#   3. persist_directory 设置后会自动写盘 → 下次直接 Chroma(persist_directory=...) 就能加载
#      不用重新 embed（embedding 调用是要花钱的，避免重复非常关键）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(DATA_DIR / "chroma_db"),
)


# ============================================================
# Step 4：检索器（MMR）
# ============================================================
# .as_retriever() 把 vectorstore 包装成 Runnable —— 这是关键，下一步才能用 | 串联。
#
# 为什么用 MMR 而不是 similarity？
# - similarity 只看相关性，结果可能 4 条都是同一段话被切到不同 chunk 的近似副本
# - MMR 在挑每条结果时会"减去与已选结果的相似度"，强制多样性
# - 实际效果：4 条 Top-K 覆盖更广，LLM 拿到的上下文信息密度更高
#
# fetch_k 是 MMR 的候选池大小（先取 10 个最相似的，再用 MMR 挑出 4 个多样化的）。
# 经验值：fetch_k = 2-3 倍的 k。详见 ../05_retriever/02_mmr_retriever.py
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 10},
)


# ============================================================
# Step 5：上下文格式化函数
# ============================================================
# 检索器返回的是 List[Document]，但 prompt 模板的 {context} 变量只能接收字符串。
# 所以需要一个"摆渡函数"把 Document 列表拼成字符串。
#
# 这个 format_docs 看似简单，工程上有讲究：
# - 用分隔符（"\n\n---\n\n"）把不同片段隔开 → 帮助 LLM 区分独立的资料来源
# - 标注片段编号 → 后续要让 LLM 引用来源时，可以让它输出 "[文档片段 2]" 之类
# - 真实生产里通常还会带上 metadata（文件名、页码）方便追溯
def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[文档片段 {i + 1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


# ============================================================
# Step 6：Prompt 模板
# ============================================================
# RAG Prompt 的三要素：
#   1. system 角色定义（"你是文档问答助手"）—— 限定 LLM 的行为模式
#   2. {context} 占位符 —— 留给检索结果填充
#   3. 防幻觉指令 —— "如果资料中没有相关信息，请说明"
#      这条很关键，没有它 LLM 会自由发挥编造答案
#
# 注意 {context} 和 {question} 都是模板变量，由后面 chain 的 dict 自动填充。
RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """你是一个专业的文档问答助手。

参考资料：
{context}

请根据上述参考资料回答问题。如果资料中没有相关信息，请说明。""",
    ),
    ("human", "{question}"),
])


# ============================================================
# Step 7：组装 RAG Chain（LCEL 核心）
# ============================================================
# LCEL 的 | 操作符把多个 Runnable 串成 pipeline：
#
#   {dict}  →  prompt  →  llm  →  parser
#
# dict 的特殊语义：LangChain 会把 dict 中的每个 value 当成独立 Runnable，
# **并行执行**，再把结果按 key 拼回 dict 喂给下一步。
# 也就是说下面这个 dict 等价于：
#
#   RunnableParallel(
#       context = retriever | format_docs,    # 用 question 调用 retriever，结果格式化
#       question = RunnablePassthrough(),     # question 原样传过去（也给 prompt 用）
#   )
#
# RunnablePassthrough 就是"什么也不做、原样传递" —— 在分流场景下让原始输入
# 同时被多个分支用到。
#
# StrOutputParser 是最后的"出口"：把 AIMessage（LLM 的返回）解包成纯字符串。
# 没它的话 chain 输出会是 AIMessage 对象，调用方还要 .content 一下。
rag_chain = (
    {
        "context": retriever | format_docs,    # 检索 → 格式化
        "question": RunnablePassthrough(),     # 透传
    }
    | RAG_PROMPT                                # 用上面的 dict 填充模板变量
    | llm                                       # 喂给 LLM
    | StrOutputParser()                         # 提取 .content
)


# ============================================================
# Step 8：CLI 交互
# ============================================================
# .invoke() 是同步一次性调用；如果想要边输出边显示，用 chain.stream() 替换。
# 关于 .stream / .astream / .astream_events 的用法，见 02_debug_astream_events.py
if __name__ == "__main__":
    while True:
        question = input("\n请输入问题（输入 'quit' 退出）：")
        if question.lower() == "quit":
            break
        answer = rag_chain.invoke(question)
        print(f"\n回答：{answer}")
