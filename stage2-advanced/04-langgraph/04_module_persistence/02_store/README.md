# Store 示例

LangGraph 的 `Store` 用来存「跨 thread / 长期记忆」—— Checkpointer 只能让同一个
`thread_id` 续聊，Store 则能让 graph **跨会话、跨用户**记住事实、偏好、向量化的检索文档。

## 示例

| 脚本 | Store 实现 | 需要容器 | 演示重点 |
| --- | --- | --- | --- |
| `01_basic_operations.py` | `InMemoryStore` | ❌ 无 | put / get / search 基础 API |
| `02_semantic_search_config.py` | `InMemoryStore` + embeddings | ❌ 无 | 索引配置（dims / fields） |
| `03_semantic_search_demo.py` | `InMemoryStore` + embeddings | ❌ 无 | 语义检索完整流程 |
| `04_postgres_store.py` | `PostgresStore` + **PGVector** | ✅ postgres（**带 pgvector**） | 生产可用的持久化向量 Store |

> 1–3 全部是 `InMemoryStore`，无需任何外部依赖，开箱即跑。
> 只有 04 需要 Postgres + pgvector 扩展。

## Postgres 容器（与 01_checkpointer 共用）

**关键点**：`PostgresStore.setup()` 会执行 `CREATE EXTENSION IF NOT EXISTS vector`，
**vanilla `postgres:16` 镜像没有 pgvector**，必须用 `pgvector/pgvector:pg16`。

`01_checkpointer/README.md` 里建容器的命令已经统一改成 pgvector 镜像，**同一个容器**
同时服务两边：

```bash
docker run -d --name langgraph-pg \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=langgraph \
  -p 5432:5432 pgvector/pgvector:pg16
```

container 起来后，**额外建一个 store 专用的库**（脚本里 URI 是 `langgraph_store`）：

```bash
DOCKER=/Applications/Docker.app/Contents/Resources/bin/docker
$DOCKER exec langgraph-pg psql -U user -d langgraph -c "CREATE DATABASE langgraph_store;"
$DOCKER exec langgraph-pg psql -U user -d langgraph_store -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

> 也可以让 store 和 checkpointer 共用同一个 `langgraph` 库（表名不冲突），把 04 脚本里
> 的 URI 末尾改成 `/langgraph` 即可。当前用 `langgraph_store` 主要是为了示例清晰。

## .env 需要的项

```env
DB_URI=postgresql://user:pass@localhost:5432/langgraph
DB_URI_STORE=postgresql://user:pass@localhost:5432/langgraph_store
OPENAI_API_KEY=sk-...   # OpenAIEmbeddings 用；可替换成本地 / dashscope embeddings
```

## 跑示例

```bash
uv run python stage2-advanced/04-langgraph/04_module_persistence/02_store/01_basic_operations.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/02_store/02_semantic_search_config.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/02_store/03_semantic_search_demo.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/02_store/04_postgres_store.py
```

## 踩坑提示

- **`could not open extension control file "vector.control"`** —— 用错镜像了。
  必须 `pgvector/pgvector:pg16`，不能 `postgres:16`。换镜像要 `docker rm -f langgraph-pg`
  再 `docker run`，老数据会丢（练习数据无所谓）。
- **`database "langgraph_store" does not exist`** —— 上面那条 `CREATE DATABASE` 没跑。
- **OpenAIEmbeddings 401** —— `.env` 缺 `OPENAI_API_KEY`，或想用国内 embeddings
  可换成 `DashScopeEmbeddings(model="text-embedding-v3")`。

## 验证 store 真的落了数据

```bash
DOCKER=/Applications/Docker.app/Contents/Resources/bin/docker
$DOCKER exec langgraph-pg psql -U user -d langgraph_store -c "\dt"
$DOCKER exec langgraph-pg psql -U user -d langgraph_store -c \
  "SELECT prefix, key FROM store LIMIT 5;"
```
