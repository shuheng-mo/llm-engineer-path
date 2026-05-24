"""5.4 CRUD 实战 — 增 / 查 / 改 / 删

合并自原 docx 块 22 (Create) / 23 (Read) / 24 (Update) / 25 (Delete)。
额外补充 get_book_by_id (按 ID 查询，测试用例中需要)。
"""

from typing import Optional

from sqlmodel import select

from orm.database import async_session
from orm.models import Book


async def create_book(book_data: Book) -> Book:
    """创建新图书，返回包含自动生成 id 的 Book 对象"""
    async with async_session() as session:
        session.add(book_data)
        await session.commit()
        await session.refresh(book_data)
        return book_data


async def get_books() -> list[Book]:
    """查询所有图书"""
    async with async_session() as session:
        statement = select(Book)
        result = await session.execute(statement)
        return result.scalars().all()


async def get_book_by_id(book_id: int) -> Optional[Book]:
    """按 ID 查询单本图书 (test_crud.py 需要)"""
    async with async_session() as session:
        return await session.get(Book, book_id)


async def update_book(book_id: int, new_data: Book) -> Optional[Book]:
    """更新图书信息，返回更新后的 Book；不存在时返回 None"""
    async with async_session() as session:
        book = await session.get(Book, book_id)
        if not book:
            return None
        book.title = new_data.title
        book.author = new_data.author
        book.price = new_data.price
        if new_data.description:
            book.description = new_data.description
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book


async def delete_book(book_id: int) -> bool:
    """删除图书；不存在返回 False"""
    async with async_session() as session:
        book = await session.get(Book, book_id)
        if not book:
            return False
        await session.delete(book)
        await session.commit()
        return True
