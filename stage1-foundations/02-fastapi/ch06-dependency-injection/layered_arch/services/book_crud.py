"""6.5 企业级架构分层 — Service 层 (纯业务逻辑)

设计原则：
- 不依赖 HTTP 请求上下文 (Request / Header / status_code 这些都不该出现)
- session 由调用方传入，service 不关心 session 哪里来的
- 返回 ORM 对象或基础类型，不返回 fastapi 的 Response
- 不存在/失败时返回 None / False / 抛业务异常 (ValueError)；
  由 router 层翻译成 HTTPException / 状态码

这样 service 层可以被 CLI、定时任务、后台 worker、单元测试等多种入口复用，
不只服务 HTTP 路由。
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from orm.models import Book


async def create_book(session: AsyncSession, book: Book) -> Book:
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def get_all_books(session: AsyncSession) -> list[Book]:
    result = await session.execute(select(Book))
    # .scalars().all() 返回的是 Sequence[Book]，显式转 list 让 FastAPI 类型推导清晰
    return list(result.scalars().all())


async def get_book_by_id(session: AsyncSession, book_id: int) -> Optional[Book]:
    return await session.get(Book, book_id)


async def delete_book(session: AsyncSession, book_id: int) -> bool:
    """删除成功返回 True；不存在返回 False (由 router 翻译成 404)"""
    book = await session.get(Book, book_id)
    if not book:
        return False
    await session.delete(book)
    await session.commit()
    return True
