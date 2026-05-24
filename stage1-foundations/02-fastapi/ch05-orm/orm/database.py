"""5.3 / 6.3 数据库连接与异步 Session 配置

本文件同时服务 ch05 和 ch06，两种模式可同时存在、互不影响：
  - ch05 CRUD 单元测试 (test_crud.py) — 直接用 `async_session()` 当 context manager
  - ch06 FastAPI 路由 (07_use_session_in_route.py) — 通过 `Depends(get_session)` 注入

数据库文件统一放在 `02-fastapi/data/books.db` (用 `Path(__file__)` 算绝对路径)，
不论从哪个章节运行都指向同一份，避免相对路径切来切去。

两种用法核心区别：

┌────────────────┬───────────────────────────────┬───────────────────────────────┐
│                │ ch05 模式                      │ ch06 模式                      │
├────────────────┼───────────────────────────────┼───────────────────────────────┤
│ 谁管 session   │ 调用方 (crud.py 自己)         │ FastAPI 框架替你管             │
│ 调用方式       │ async with async_session():   │ Depends(get_session) 注入      │
│ 生命周期       │ with 语句作用域内             │ 整个请求范围 (yield 前/后)     │
│ 适用场景       │ 脚本、单元测试、后台任务      │ HTTP 路由处理函数              │
│ 是否需 yield   │ 否                            │ 是 (才能让 FastAPI 接管)        │
└────────────────┴───────────────────────────────┴───────────────────────────────┘
"""

from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# ─── 数据库文件位置 (跨章节统一) ─────────────────────────────────────────────
# parents[0]=orm, parents[1]=ch05-orm, parents[2]=02-fastapi
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "books.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# 网络数据库示例 (需装对应驱动)：
#   "mysql+aiomysql://root:pwd@localhost:3306/books_db?charset=utf8mb4"

# ─── 异步引擎 + Session 工厂 (两种模式共用) ────────────────────────────────
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 打印 SQL 语句（开发用；生产建议关掉）
    future=True,  # 启用 SQLAlchemy 2.0 特性
)

# async_sessionmaker 是 Session 工厂，每次调用 `async_session()` 返回一个新 session。
# expire_on_commit=False: commit 后对象属性仍可访问，否则要重新查（开发更友好）。
# class_=AsyncSession: 必须与异步引擎匹配，同步版叫 Session。
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── 表初始化 (两种模式共用) ────────────────────────────────────────────────
async def init_db():
    """创建所有已注册到 SQLModel.metadata 的表 (应用启动时调用一次)。

    本函数内部主动 import orm.models 触发 `class Book(...)` 执行，
    从而把 Book 注册进 SQLModel.metadata，再调 create_all 建表。
    这样调用方 (main.py / test_crud.py) 只要 `await init_db()` 即可，
    不需要为了"建表"再去显式 import models 制造一个看似无用的导入。
    """
    from orm import models as _models  # noqa: F401  # 副作用：注册 Book 到 metadata

    _ = _models  # 显式引用，避免静态分析器误报"未使用"
    async with engine.begin() as conn:
        # 如需重建表，先打开下一行
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


# ─── 【ch06 用法】FastAPI 依赖项 get_session ───────────────────────────────
# ch05 不会调用这个函数 (crud.py 直接用 async_session 当 context manager)；
# ch06 路由通过 Depends(get_session) 注入。两种用法零冲突，函数始终在这里待命。
#
# 用法示例（注释，仅作参考）：
#   from fastapi import Depends
#   from orm.database import get_session
#
#   @app.post("/books/")
#   async def create(book: Book, session: AsyncSession = Depends(get_session)):
#       session.add(book); await session.commit()
#
# 为什么用 yield？
#   FastAPI 看到生成器依赖时，会在请求开始时 `next(gen)` 拿到 yield 出来的值
#   注入给路由；请求结束 (无论成功还是异常) 再 `next(gen)` 触发 yield 之后的
#   清理代码 — 这里 `async with` 退出时会自动 close session。一行 yield 实现
#   "请求级 session" 的标准模式，对应 ch06 的 "yield 实现依赖" 知识点。
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
