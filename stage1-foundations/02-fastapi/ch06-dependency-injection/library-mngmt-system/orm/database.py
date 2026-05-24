"""数据库引擎 / Session 工厂 / 依赖项

职责：
  1. 创建异步数据库引擎 (engine)
  2. 创建异步 Session 工厂 (async_session)
  3. 提供 init_db()：应用启动时建表
  4. 提供 get_session()：FastAPI 依赖注入，给每个请求一个独立 Session
"""

from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

# ── 数据库连接 URL ──────────────────────────────────────────────
# 用 Path(__file__) 算绝对路径，无论从哪个 cwd 启动都指向同一个文件
# DB 文件放在 project/data/books.db (不混进代码目录 orm/)
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{_DATA_DIR / 'books.db'}"

# ── 1. 异步引擎 ────────────────────────────────────────────────
# echo=True   → 把每条 SQL 打印到控制台，方便开发调试
# future=True → 启用 SQLAlchemy 2.0 新特性
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

# ── 2. 异步 Session 工厂 ───────────────────────────────────────
# expire_on_commit=False → commit 后对象属性仍可访问
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── 3. 初始化数据库（建表）────────────────────────────────────
async def init_db() -> None:
    """扫描所有 SQLModel 模型，创建对应的表 (幂等)。"""
    # 副作用 import：触发 Book 类定义，注册到 SQLModel.metadata
    from . import models as _models  # noqa: F401

    _ = _models
    async with engine.begin() as conn:
        # run_sync：把同步的 create_all 适配到异步连接中执行
        await conn.run_sync(SQLModel.metadata.create_all)


# ── 4. FastAPI 依赖项：每个请求独立 Session ─────────────────────
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """配合 Depends(get_session) 注入到路由函数。

    工作原理 (yield 生成器):
      1. 请求进来 → 创建一个新 Session
      2. yield session → 把 Session 交给路由函数使用
      3. 路由函数执行完毕 → 回到这里，async with 自动关闭 Session
      4. 即使路由函数抛出异常，Session 也会被正确关闭 (不会泄漏连接)
    """
    async with async_session() as session:
        yield session  # ← 暂停点：路由函数在这里拿到 session 并使用
        # yield 之后：session 随 async with 块结束自动关闭
