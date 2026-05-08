"""PostgreSQL 短期记忆 — PostgresChatMessageHistory

对应课程章节：第七章 / 3.3 Postgres 存储
"""
import os

from langchain_community.chat_message_histories import PostgresChatMessageHistory


def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    pg_host = os.getenv("PG_HOST")
    pg_port = os.getenv("PG_PORT")
    pg_db = os.getenv("PG_DB")
    pg_user = os.getenv("PG_USER")
    pg_password = os.getenv("PG_PASSWORD")

    connection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

    return PostgresChatMessageHistory(
        session_id=session_id,
        connection_string=connection_string,
        table_name="chat_history",
    )
