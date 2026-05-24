"""6.5 企业级架构分层 — 主应用 (串起 router + service + ORM)

分层关系：
    HTTP 请求
       │
       ▼
    routers/books.py     ← HTTP 层 (参数解析、状态码翻译、依赖注入)
       │ 调用
       ▼
    services/book_crud.py  ← Service 层 (纯业务逻辑、可被任意入口复用)
       │ 调用
       ▼
    orm/models.py + orm/database.py  ← 数据层 (来自 ch05-orm)

运行:
    cd stage1-foundations/02-fastapi/ch06-dependency-injection/layered_arch
    uv run uvicorn main:app --reload

测试 (在另一终端):
    # 新增
    curl -X POST http://127.0.0.1:8000/books/ \\
      -H "Content-Type: application/json" \\
      -d '{"title":"分层架构","author":"Eric Evans","price":99.0}'

    # 列表
    curl http://127.0.0.1:8000/books/

    # 详情
    curl http://127.0.0.1:8000/books/1

    # 删除
    curl -X DELETE http://127.0.0.1:8000/books/1

    # 不存在的 ID → 404
    curl -i http://127.0.0.1:8000/books/9999
"""

# 把 ch05-orm/ 加入 sys.path，让本目录可以 import orm.* (与 ch06/07 同一套路)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ch05-orm"))

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402

from orm.database import init_db  # noqa: E402
from routers.books import router as books_router  # noqa: E402

# 注：models 不在这里 import，由 init_db() 内部自己触发 — 避免了"看似无用"的导入


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """启动时建表 (如不存在)，关闭时无需特殊清理。

    lifespan 函数签名必须接 app 参数，但本例用不到 — `_` 前缀表明刻意忽略。
    """
    await init_db()
    yield


app = FastAPI(title="企业级分层架构 demo", lifespan=lifespan)
app.include_router(books_router)


@app.get("/", tags=["首页"])
async def root():
    return {
        "message": "分层架构 demo",
        "structure": "router → service → orm",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
