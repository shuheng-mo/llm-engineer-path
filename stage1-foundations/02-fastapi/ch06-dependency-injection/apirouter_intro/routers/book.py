"""6.4 APIRouter 三步骤 — 步骤 1+2: 创建子路由 & 定义接口"""

from typing import Dict

from fastapi import APIRouter

# 创建一个名为 book_router 的子路由对象
book_router = APIRouter()


# 1. 新增书籍接口 (POST)
@book_router.post("/books/")
async def create_book(title: str, author: str) -> Dict:
    """新增一本图书"""
    return {"message": "书籍创建成功", "data": {"title": title, "author": author}}


# 2. 查询所有书籍 (GET)
@book_router.get("/books/")
async def get_all_books() -> Dict:
    """查询图书馆里所有的书"""
    return {"message": "查询成功", "data": [{"id": 1, "title": "Python入门", "author": "张三"}]}


# 3. 查询单本书籍 (GET + 路径参数)
@book_router.get("/books/{book_id}")
async def get_book(book_id: int) -> Dict:
    """根据 ID 查询一本书"""
    return {"message": "查询成功", "data": {"id": book_id, "title": "特定书籍", "author": "李四"}}
