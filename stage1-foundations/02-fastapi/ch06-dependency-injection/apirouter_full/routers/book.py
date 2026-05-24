"""6.4.3 完整项目结构示例 — routers/book.py"""

from typing import Dict

from fastapi import APIRouter

# 步骤1: 创建子路由
book_router = APIRouter()


# 步骤2: 定义接口
# 1. 新增书籍接口（POST 请求）
@book_router.post("/books/")
async def create_book(title: str, author: str) -> Dict:
    """新增一本图书"""
    return {"message": "书籍创建成功", "data": {"title": title, "author": author}}


# 2. 查询所有书籍接口（GET 请求）
@book_router.get("/books/")
async def get_all_books() -> Dict:
    """查询图书馆里所有的书"""
    # 实际项目中这里会从数据库查询
    return {"message": "查询成功", "data": [{"id": 1, "title": "Python入门", "author": "张三"}]}


# 3. 查询单本书籍接口（GET 请求，带路径参数）
@book_router.get("/books/{book_id}")
async def get_book(book_id: int) -> Dict:
    """根据ID查询一本书"""
    return {"message": "查询成功", "data": {"id": book_id, "title": "特定书籍", "author": "李四"}}
