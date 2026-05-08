"""RunnablePassthrough — 数据透传（RAG 场景同时保留原始输入和检索结果）

对应课程章节：第六章 / 3.5
"""
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = os.getenv("DASHSCOPE_MODEL_NAME") or "qwen-max"

model = ChatOpenAI(api_key=api_key, base_url=base_url, model=model_name, temperature=0)


def retrieve_docs(query: str) -> str:
    return f"[检索结果] 关于 '{query}' 的相关文档..."


parallel = RunnableParallel({
    "context": RunnableLambda(lambda x: retrieve_docs(x["question"])),
    "question": RunnablePassthrough(),
})

prompt = ChatPromptTemplate.from_template(
    """根据以下上下文回答问题：

上下文：{context}

问题：{question}

回答："""
)

rag_chain = parallel | prompt | model

mid = parallel.invoke({"question": "什么是 LangChain？"})
print(mid)

result = rag_chain.invoke({"question": "什么是 LangChain？"})
print(result)
