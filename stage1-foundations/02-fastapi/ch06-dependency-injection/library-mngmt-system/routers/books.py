"""路由层 (Router Layer)

职责：
  - 接收 HTTP 请求，校验路径/查询参数
  - 通过 Depends 获取数据库 Session
  - 调用 Service 层的函数处理业务
  - 返回 HTTP 响应 (含正确状态码)

严禁在路由层直接写数据库操作！
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import services.book_crud as book_crud
from orm.database import get_session
from orm.models import Book

# ── 创建子路由 ──────────────────────────────────────────────────
# prefix="/books"   → 该路由下所有接口路径都以 /books 开头
# tags=["图书管理"] → Swagger 文档中的分组标签
book_router = APIRouter(prefix="/books", tags=["图书管理"])


# ── 分页参数提取依赖 ─────────────────────────────────────────────
async def pagination_params(
    skip: int = Query(default=0, ge=0, description="跳过前 N 条记录 (分页偏移量)"),
    limit: int = Query(default=10, ge=1, le=100, description="每页返回条数，最大 100"),
) -> dict:
    """提取通用分页参数的依赖函数，路由通过 Depends 调用"""
    return {"skip": skip, "limit": limit}


# ── POST /books/ ：录入新书 ─────────────────────────────────────
@book_router.post(
    "/",
    response_model=Book,  # 告诉 FastAPI 响应数据的结构
    status_code=201,  # 创建成功习惯用 201 状态码
    summary="录入新书",
)
async def create_book(
    book: Book,  # 请求体：从 JSON 自动解析成 Book 对象
    session: AsyncSession = Depends(get_session),  # 依赖注入：自动获取 Session
):
    """录入一本新书到数据库。

    - **title**：书名 (必填)
    - **author**：作者 (必填)
    - **price**：定价，必须 > 0 (必填)
    - **publish_date**：出版日期，格式 YYYY-MM-DD (可选)
    - **description**：简介 (可选)
    """
    return await book_crud.create_book(session, book)


# ── GET /books/ ：查询图书列表 ─────────────────────────────────
@book_router.get(
    "/",
    response_model=list[Book],
    summary="查询图书列表 (支持模糊搜索 + 分页)",
)
async def get_books(
    title: Optional[str] = Query(default=None, description="按书名模糊搜索关键词"),
    pagination: dict = Depends(pagination_params),  # 分页参数通过 Depends 注入
    session: AsyncSession = Depends(get_session),  # Session 通过 Depends 注入
):
    """查询图书列表。

    - 不传 **title** → 返回所有图书
    - 传入 **title** → 按书名模糊匹配 (不区分前后缀)
    - **skip** / **limit** 控制分页
    """
    return await book_crud.get_books(
        session=session,
        title_keyword=title,
        skip=pagination["skip"],
        limit=pagination["limit"],
    )


# ── GET /books/{book_id} ：查询单本详情 ────────────────────────
@book_router.get(
    "/{book_id}",
    response_model=Book,
    summary="查询单本图书详情",
)
async def get_book(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    """根据图书 ID 查询详情。

    - 找到 → 返回 Book 对象 (200)
    - 找不到 → 返回 404 错误
    """
    book = await book_crud.get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"图书 ID={book_id} 不存在")
    return book


# ── PUT /books/{book_id} ：更新图书信息 ────────────────────────
@book_router.put(
    "/{book_id}",
    response_model=Book,
    summary="更新图书信息",
)
async def update_book(
    book_id: int,
    new_data: Book,  # 请求体：新数据
    session: AsyncSession = Depends(get_session),
):
    """更新指定 ID 的图书信息 (全量更新)。

    - 找到并更新 → 返回更新后的 Book 对象 (200)
    - 找不到 → 返回 404 错误
    """
    updated = await book_crud.update_book(session, book_id, new_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"图书 ID={book_id} 不存在，无法更新")
    return updated


# ── DELETE /books/{book_id} ：删除图书 ─────────────────────────
@book_router.delete(
    "/{book_id}",
    status_code=200,
    summary="删除图书",
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除指定 ID 的图书。

    - 删除成功 → 返回成功消息 (200)
    - 找不到 → 返回 404 错误
    """
    success = await book_crud.delete_book(session, book_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"图书 ID={book_id} 不存在，无法删除")
    return {"message": f"图书 ID={book_id} 已成功删除"}
