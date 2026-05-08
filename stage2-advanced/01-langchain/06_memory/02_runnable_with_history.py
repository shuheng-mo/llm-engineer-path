"""RunnableWithMessageHistory — 把 Runnable 包装成可记忆链

对应课程章节：第七章 / 3.2
"""
import os

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
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

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的AI助手，请记住用户告诉你的信息。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

runnable = prompt | llm

store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


chain_with_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "user_001"}}

response1 = chain_with_history.invoke(
    {"input": "你好，我叫小明，我是一名Python程序员"},
    config=config,
)
print(f"AI: {response1.content}")

response2 = chain_with_history.invoke(
    {"input": "我叫什么名字？我的职业是什么？"},
    config=config,
)
print(f"AI: {response2.content}")
