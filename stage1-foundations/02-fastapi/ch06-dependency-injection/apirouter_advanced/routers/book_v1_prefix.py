"""6.4.4 高级玩法 — 使用 prefix 统一路径前缀"""

from fastapi import APIRouter

# 创建子路由时，指定统一的路径前缀 /books
book_router = APIRouter(prefix="/books")


# 定义接口时，路径就可以省略前缀了！
@book_router.post("/")  # 实际访问路径是: POST /books/
async def create_book(title: str, author: str):
    return {"message": "书籍创建成功", "data": {"title": title, "author": author}}


@book_router.get("/")  # 实际访问路径是: GET /books/
async def get_all_books():
    return {"message": "查询成功", "data": [{"id": 1, "title": "Python入门", "author": "张三"}]}


@book_router.get("/{book_id}")  # 实际访问路径是: GET /books/{book_id}
async def get_book(book_id: int):
    return {"message": "查询成功", "data": {"id": book_id, "title": "特定书籍", "author": "李四"}}
