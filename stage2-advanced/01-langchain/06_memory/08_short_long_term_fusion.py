"""短期 + 长期记忆融合 — RunnableWithMessageHistory + 向量库注入

对应课程章节：第七章 / 4.4
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

vectorstore = Chroma(
    collection_name="long_term_memory",
    embedding_function=embeddings,
)

session_store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


def get_long_term_memory(user_id: str, query: str) -> str:
    results = vectorstore.similarity_search(query, k=3, filter={"user_id": user_id})
    if not results:
        return "暂无长期记忆"
    return "\n".join(f"- {doc.page_content}" for doc in results)


prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手。

## 用户长期记忆（背景信息）
{long_term_memory}

请根据以上信息为用户提供个性化帮助。"""),
    MessagesPlaceholder(variable_name="history"),         # 短期记忆
    ("human", "{input}"),
])


def create_chain_with_long_term_memory(user_id: str):
    def inject_long_term_memory(inputs: dict) -> dict:
        return {**inputs, "long_term_memory": get_long_term_memory(user_id, inputs["input"])}

    base_chain = inject_long_term_memory | prompt | llm | StrOutputParser()

    return RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )


user_chain = create_chain_with_long_term_memory("user_001")
config = {"configurable": {"session_id": "session_001"}}

response = user_chain.invoke({"input": "帮我写一段处理用户订单的代码"}, config=config)
print(response)
