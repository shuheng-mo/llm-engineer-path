"""服务层 (Service Layer)

职责：封装所有数据库 CRUD 操作，不关心 HTTP 请求/响应细节。
路由层只调用这里的函数，不直接写数据库操作。
"""

from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from orm.models import Book


# ── CREATE ──────────────────────────────────────────────────────
async def create_book(session: AsyncSession, book: Book) -> Book:
    """将一本新书写入数据库。

    流程：
      1. session.add(book)         → 把对象加入会话 (标记为"待保存")
      2. await session.commit()    → 执行 INSERT SQL，真正写入数据库
      3. await session.refresh(book) → 重新从数据库读取，拿到自动生成的 id
    """
    # JSON 里 date 通常是字符串，手动转 date 对象
    if isinstance(book.publish_date, str):
        book.publish_date = date.fromisoformat(book.publish_date)
    session.add(book)
    await session.commit()
    await session.refresh(book)  # 刷新后 book.id 就有值了
    return book


# ── READ：查询列表（支持模糊搜索 + 分页）────────────────────────
async def get_books(
    session: AsyncSession,
    title_keyword: Optional[str],  # 书名关键词（可为空）
    skip: int,  # 跳过前 skip 条（分页偏移）
    limit: int,  # 最多返回 limit 条
) -> list[Book]:
    """查询图书列表，支持按书名模糊搜索 + 分页。"""
    statement = select(Book)

    # 如果传入了关键词，拼接 WHERE title LIKE '%keyword%'
    if title_keyword:
        statement = statement.where(Book.title.contains(title_keyword))

    # 分页：跳过 skip 条，取 limit 条
    statement = statement.offset(skip).limit(limit)

    result = await session.execute(statement)
    # scalars() → 把结果行转成 Book 对象列表 (而不是原始 Row 对象)
    return list(result.scalars().all())


# ── READ：查询单本 ───────────────────────────────────────────────
async def get_book_by_id(session: AsyncSession, book_id: int) -> Optional[Book]:
    """根据主键 ID 查询一本书。找不到返回 None，路由层翻译成 404。"""
    return await session.get(Book, book_id)


# ── UPDATE ───────────────────────────────────────────────────────
async def update_book(
    session: AsyncSession,
    book_id: int,
    new_data: Book,
) -> Optional[Book]:
    """更新指定 ID 的图书信息。先查 → 逐字段覆盖 → 提交 → 刷新。"""
    book = await session.get(Book, book_id)
    if not book:
        return None

    # 必填字段：覆盖
    book.title = new_data.title
    book.author = new_data.author
    book.price = new_data.price

    # 可选字段：客户端明确传了才覆盖
    if new_data.publish_date is not None:
        if isinstance(new_data.publish_date, str):
            book.publish_date = date.fromisoformat(new_data.publish_date)
        else:
            book.publish_date = new_data.publish_date
    if new_data.description is not None:
        book.description = new_data.description

    session.add(book)  # 标记为"已修改"
    await session.commit()
    await session.refresh(book)
    return book


# ── DELETE ───────────────────────────────────────────────────────
async def delete_book(session: AsyncSession, book_id: int) -> bool:
    """删除指定 ID 的图书。成功返回 True，不存在返回 False。"""
    book = await session.get(Book, book_id)
    if not book:
        return False
    await session.delete(book)
    await session.commit()
    return True
