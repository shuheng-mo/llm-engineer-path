"""PostgresStore — 生产环境推荐（PGVector 向量搜索）

对应课程章节：模块四 / 3.4.1

依赖:
uv pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres
"""

from langchain_openai import OpenAIEmbeddings
from langgraph.store.postgres import PostgresStore

DB_URI = "postgresql://user:pass@localhost:5432/langgraph_store"

with PostgresStore.from_conn_string(DB_URI) as store:
    store.setup()  # 创建表 + 启用 PGVector
    embeddings = OpenAIEmbeddings()

    # graph = builder.compile(store=store, checkpointer=checkpointer)
