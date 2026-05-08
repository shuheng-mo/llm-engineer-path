"""Redis 短期记忆 — RedisChatMessageHistory（生产环境推荐）

对应课程章节：第七章 / 3.3 Redis 存储
"""
import os

from langchain_community.chat_message_histories import RedisChatMessageHistory


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_db = os.getenv("REDIS_DB", "0")

    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
    return RedisChatMessageHistory(session_id=session_id, url=redis_url)
