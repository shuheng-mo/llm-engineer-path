"""Multi-Query 自定义实现 — 自己控制 Prompt + 去重逻辑

对应课程章节：二 / 2.4 方式二
"""
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.7,
)

multi_query_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """你的任务是生成 3 个不同角度的搜索查询，帮助更全面地检索相关文档。

【要求】
- 每个查询从不同角度切入（如：定义、原理、对比、应用）
- 用换行分隔，不要编号
- 直接输出查询，无需解释

【示例】
原问题：什么是机器学习？
输出：
机器学习 定义 概念
机器学习 算法 原理 工作方式
机器学习 应用场景 案例""",
    ),
    ("human", "原问题：{question}"),
])


def generate_queries(question: str) -> list:
    response = (multi_query_prompt | llm).invoke({"question": question})
    return [q.strip() for q in response.content.strip().split("\n") if q.strip()]


def multi_query_retrieve(question: str, retriever, k: int = 3) -> list:
    queries = generate_queries(question)
    print(f"生成的查询变体: {queries}")

    all_docs = []
    seen_contents = set()
    for query in queries:
        for doc in retriever.invoke(query):
            content_key = doc.page_content[:100]
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                all_docs.append(doc)
    return all_docs[: k * 2]


if __name__ == "__main__":
    # 假设外部已经准备好 base_retriever
    from langchain_chroma import Chroma
    from langchain_community.embeddings import DashScopeEmbeddings

    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    print(multi_query_retrieve("什么是 RAG？", base_retriever))
