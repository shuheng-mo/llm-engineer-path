"""Multi-Query 内置版 — MultiQueryRetriever.from_llm

对应课程章节：二 / 2.4 方式一
"""
import os
from dotenv import load_dotenv
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.7,            # 稍高，让生成的查询更多样
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

vectorstore = Chroma(persist_directory=str(DATA_DIR / "chroma_db"), embedding_function=embeddings)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

multi_retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

results = multi_retriever.invoke("什么是 RAG？")
print(results)
