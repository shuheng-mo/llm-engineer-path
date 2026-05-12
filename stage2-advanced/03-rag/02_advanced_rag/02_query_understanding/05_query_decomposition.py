"""查询分解（Query Decomposition） — 把复杂问题拆成可独立检索的子问题

对应课程章节：二 / 2.6
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)

decompose_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """将复杂问题分解为 2-4 个可以独立回答的简单子问题。

【要求】
- 每个子问题应该可以通过单次检索回答
- 子问题要覆盖原问题的所有方面
- 以 JSON 数组格式输出

【示例】
原问题：对比 A 和 B 的优缺点，哪个更适合场景 X？
输出：["A 的特点和优势", "B 的特点和优势", "A 和 B 的对比", "场景 X 的需求"]""",
        ),
        ("human", "{question}"),
    ]
)


def decompose_query(question: str) -> list:
    response = (decompose_prompt | llm).invoke({"question": question})
    try:
        return json.loads(response.content)
    except Exception:
        return [question]


def decomposed_rag(question: str, retriever, rag_chain) -> str:
    sub_questions = decompose_query(question)
    print(f"分解为 {len(sub_questions)} 个子问题:")
    for i, sq in enumerate(sub_questions, 1):
        print(f"  {i}. {sq}")

    sub_answers = []
    for sq in sub_questions:
        answer = rag_chain.invoke(sq)
        sub_answers.append(f"【{sq}】\n{answer}")

    summary_prompt = f"""基于以下子问题的回答，综合回答原始问题。

原始问题：{question}

子问题回答：
{chr(10).join(sub_answers)}

请给出综合分析和最终建议："""

    return llm.invoke(summary_prompt).content


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个专业的文档问答助手。

参考资料：
{context}

请根据上述参考资料回答问题。如果资料中没有相关信息，请说明。""",
        ),
        ("human", "{question}"),
    ]
)


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[文档片段 {i + 1}]\n{doc.page_content}" for i, doc in enumerate(docs)
    )


if __name__ == "__main__":
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    vectorstore = Chroma(
        persist_directory=str(DATA_DIR / "chroma_db"),
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    complex_question = "对比LangChain和LlamaIndex,哪个更适合构建客服问答系统"
    answer = decomposed_rag(complex_question, retriever=retriever, rag_chain=rag_chain)
    print(answer)
