"""6.5 企业级架构分层 — Service 层 (纯业务逻辑)"""

from sqlalchemy.ext.asyncio import AsyncSession
from orm import Book


async def create_book(session: AsyncSession, book: Book):  # 纯粹的业务逻辑，不依赖 HTTP 请求上下文
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book
