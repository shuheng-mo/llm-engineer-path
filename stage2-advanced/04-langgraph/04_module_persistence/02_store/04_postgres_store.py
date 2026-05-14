"""PostgresStore — 生产环境推荐（PGVector 向量搜索）

对应课程章节：模块四 / 3.4.1

依赖:
    uv pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres

要点:
- 容器必须用 `pgvector/pgvector:pg16`（不是 vanilla `postgres:16`），
  否则 `store.setup()` 里的 `CREATE EXTENSION vector` 会失败。
- 数据库 `langgraph_store` 需提前建好：
  `docker exec langgraph-pg psql -U user -d langgraph -c "CREATE DATABASE langgraph_store;"`
- 这里用 dashscope 的 `text-embedding-v3` 通过 OpenAI 兼容协议接入，避免依赖
  OPENAI_API_KEY。要换成真正的 OpenAI，把 base_url 删掉即可。
"""

import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langgraph.store.postgres import PostgresStore
from langgraph.store.postgres.base import PostgresIndexConfig
from pydantic import SecretStr

load_dotenv()

DB_URI = "postgresql://user:pass@localhost:5432/langgraph_store"

# dashscope text-embedding-v3 是 1024 维。
# check_embedding_ctx_length=False 关掉 tiktoken 分词路径 —— OpenAIEmbeddings 默认
# 会先把文本编码成 token id 数组再调 API，DashScope 兼容端点不认这种格式，必须传字符串。
embeddings = OpenAIEmbeddings(
    model="text-embedding-v3",
    api_key=SecretStr(os.environ["DASHSCOPE_API_KEY"]),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    check_embedding_ctx_length=False,
)

index_config: PostgresIndexConfig = {
    "dims": 1024,
    "embed": embeddings,
    "fields": ["text"],  # 对 value["text"] 做向量化
}

with PostgresStore.from_conn_string(DB_URI, index=index_config) as store:
    store.setup()  # 建表 + 启 PGVector（首次幂等）

    namespace = ("users", "alice", "memories")

    # 写入若干条记忆
    store.put(namespace, "m1", {"text": "Alice 喜欢喝美式咖啡"})
    store.put(namespace, "m2", {"text": "Alice 周三晚上去打羽毛球"})
    store.put(namespace, "m3", {"text": "Alice 家里有一只叫 Mochi 的橘猫"})

    # 精确取
    item = store.get(namespace, "m1")
    print(f"get m1: {item.value if item else None}")

    # 语义检索（PGVector 走 cosine 距离）
    results = store.search(namespace, query="她养了什么宠物？", limit=2)
    print("\nsemantic search 「她养了什么宠物？」:")
    for r in results:
        print(f"  [{r.key}] score={r.score:.4f}  {r.value['text']}")
