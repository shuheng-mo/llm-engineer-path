"""6.4.4 高级玩法 — 使用 tags 在文档中分组 (片段)"""

from fastapi import APIRouter

# 创建子路由时，指定标签
book_router = APIRouter(prefix="/books", tags=["书籍管理"])
