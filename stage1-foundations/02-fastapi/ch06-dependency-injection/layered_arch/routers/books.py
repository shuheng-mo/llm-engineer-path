"""6.5 企业级架构分层 — Router 层 (HTTP 关注点)

职责：
- 解析 / 校验 HTTP 输入 (依赖注入 session、Pydantic body 校验)
- 调用 service 层的纯业务函数
- 把 service 返回值 / None / False 翻译成对应 HTTP 状态码
- 选择 response_model (决定哪些字段对外暴露)

router 层不写 session.add / session.commit / select 这些 SQL 概念，
也不写 if not result: raise ... 业务判断 — 那些都在 service 里。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from orm.database import get_session
from orm.models import Book
from services import book_crud

router = APIRouter(prefix="/books", tags=["书籍 (分层架构)"])


@router.post("/", response_model=Book)
async def create_book_endpoint(
    book: Book,
    session: AsyncSession = Depends(get_session),
):
    """路由只负责"指挥"，业务实现委托给 service 层"""
    return await book_crud.create_book(session, book)


@router.get("/", response_model=list[Book])
async def list_books_endpoint(session: AsyncSession = Depends(get_session)):
    return await book_crud.get_all_books(session)


@router.get("/{book_id}", response_model=Book)
async def get_book_endpoint(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    book = await book_crud.get_book_by_id(session, book_id)
    if book is None:
        # service 返回 None → router 翻译成 404
        raise HTTPException(status_code=404, detail=f"book {book_id} not found")
    return book


@router.delete("/{book_id}")
async def delete_book_endpoint(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    ok = await book_crud.delete_book(session, book_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"book {book_id} not found")
    return {"deleted": book_id}
