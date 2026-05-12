"""完整 Redis 短期记忆实战 — RunnableWithMessageHistory + ttl

对应课程章节：第七章 / 3.3 完整 Redis
"""

import os

from dotenv import load_dotenv
from langchain_community.chat_message_histories import RedisChatMessageHistory
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

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
redis_db = os.getenv("REDIS_DB", "15")
REDIS_URL = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个友好的AI助手，请记住用户告诉你的信息。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

runnable = prompt | llm


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=3600,  # 1 小时后自动清理
    )


chain_with_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


if __name__ == "__main__":
    config = {"configurable": {"session_id": "user_001_session_001"}}

    response1 = chain_with_history.invoke(
        {"input": "你好，我叫小明，我是一名数据工程师"},
        config=config,
    )
    print(f"AI: {response1.content}")

    response2 = chain_with_history.invoke(
        {"input": "我叫什么名字？我是做什么的？"},
        config=config,
    )
    print(f"AI: {response2.content}")
