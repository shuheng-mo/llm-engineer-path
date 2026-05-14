# Checkpointer 示例

LangGraph 的 `Checkpointer` 把 graph 每一步 state 落到外部存储，用来支持
**多轮对话续聊 / 故障恢复 / 时间旅行**。本目录 6 个脚本各演示一种存储后端。

## 示例与存储后端对照

| 脚本 | 存储 | 需要容器 | 适用场景 |
| --- | --- | --- | --- |
| `01_inmemory_basic.py` | `MemorySaver`（进程内 dict） | ❌ 无 | 单元测试、demo |
| `02_inmemory_multi_turn.py` | `MemorySaver` | ❌ 无 | 演示 `thread_id` 隔离 |
| `03_postgres_sync.py` | `PostgresSaver` + 连接池 | ✅ postgres | 同步代码（CLI / 批处理 / Celery worker） |
| `04_postgres_async.py` | `AsyncPostgresSaver` | ✅ postgres（复用上面） | 异步代码（FastAPI / aiohttp） |
| `05_redis.py` | `RedisSaver` | ✅ redis（必须带 RedisSearch） | 高吞吐、TTL 友好 |
| `06_mongo.py` | `MongoDBSaver` | ✅ mongo | 文档型存储、按字段查历史 |

## 一次性启动所有依赖容器

> Docker Desktop / OrbStack 启动后再跑下面命令。`docker` 不在 PATH 时把
> `/Applications/Docker.app/Contents/Resources/bin` 加到 PATH。

```bash
# PostgreSQL —— 03 / 04 用
docker run -d --name langgraph-pg \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=langgraph \
  -p 5432:5432 postgres:16

# Redis Stack（含 RedisSearch，langgraph-checkpoint-redis 必须）—— 05 用
docker run -d --name langgraph-redis \
  -p 6379:6379 redis/redis-stack-server:latest

# MongoDB 7 —— 06 用
docker run -d --name langgraph-mongo \
  -p 27017:27017 mongo:7
```

启动后 `.env`（在 `stage2-advanced/04-langgraph/.env`）必须包含：

```env
DB_URI=postgresql://user:pass@localhost:5432/langgraph
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
MONGO_URI=mongodb://localhost:27017
```

## 跑示例

```bash
# 从 repo 根目录跑，路径前缀都一样：
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/01_inmemory_basic.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/02_inmemory_multi_turn.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/03_postgres_sync.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/04_postgres_async.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/05_redis.py
uv run python stage2-advanced/04-langgraph/04_module_persistence/01_checkpointer/06_mongo.py
```

## 各后端踩过的坑

- **Postgres `setup()` 报 `ActiveSqlTransaction`** —— `PostgresSaver.setup()`
  里用了 `CREATE INDEX CONCURRENTLY`，连接池必须传 `kwargs={"autocommit": True}`，
  否则 psycopg 默认开事务包住 DDL 会冲突。
- **Redis 报 `Cannot create index on db != 0`** —— `langgraph-checkpoint-redis`
  用 RedisSearch 建索引，索引**只能建在 db=0**。脚本里 `db=0` 不要改。
- **Redis 镜像** —— 必须用 `redis/redis-stack-server`，不是 `redis:7`。
  普通 redis 没装 RedisSearch 模块，启动 `setup()` 会失败。
- **MongoDB 无需 setup** —— `MongoDBSaver` 第一次写入时自动建集合 + 索引。

## 验证存储真的落了数据

```bash
DOCKER=/Applications/Docker.app/Contents/Resources/bin/docker

# Postgres
$DOCKER exec langgraph-pg psql -U user -d langgraph -c \
  "SELECT thread_id, COUNT(*) FROM checkpoints GROUP BY thread_id;"

# Redis
$DOCKER exec langgraph-redis redis-cli --no-raw KEYS 'checkpoint:*'

# Mongo
$DOCKER exec langgraph-mongo mongosh --quiet langgraph --eval \
  'db.checkpoints.find({}, {thread_id:1,_id:0}).limit(5).toArray()'
```

## 清理

```bash
docker rm -f langgraph-pg langgraph-redis langgraph-mongo
```

数据全部丢失，重跑会重新建表/集合 + 重新落 checkpoint，不影响示例。
