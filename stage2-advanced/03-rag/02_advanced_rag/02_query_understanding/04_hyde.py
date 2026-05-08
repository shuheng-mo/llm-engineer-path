"""HyDE（Hypothetical Document Embedding） — 用 LLM 先写假设答案再检索

对应课程章节：二 / 2.5
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()


class HyDERetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.embeddings = vectorstore._embedding_function

        self.llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.3,
        )

        self.hyde_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """根据用户问题，写一段假设性的回答文档。

【要求】
- 假设你知道答案，直接写出来
- 使用陈述句，像真实文档一样
- 100-200 字左右
- 不要说"我不知道"

【示例】
问题：什么是 RAG？
假设答案：RAG（检索增强生成）是一种结合了信息检索和文本生成的技术。它的工作原理是先从知识库中检索相关文档，然后将检索结果作为上下文提供给大语言模型，让模型基于这些真实信息生成回答。RAG 可以有效减少模型幻觉，并让模型能够访问最新的知识。""",
            ),
            ("human", "{question}"),
        ])

    def retrieve(self, question: str, k: int = 4) -> list:
        # 1. 生成假设答案
        response = (self.hyde_prompt | self.llm).invoke({"question": question})
        hypothetical_answer = response.content
        print(f"📝 假设答案: {hypothetical_answer[:100]}...")

        # 2. 用假设答案去检索
        return self.vectorstore.similarity_search(hypothetical_answer, k=k)


if __name__ == "__main__":
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    vectorstore = Chroma(persist_directory=str(DATA_DIR / "chroma_db"), embedding_function=embeddings)
    hyde_retriever = HyDERetriever(vectorstore)

    print(hyde_retriever.retrieve("怎么解决 Python 内存泄漏？"))
