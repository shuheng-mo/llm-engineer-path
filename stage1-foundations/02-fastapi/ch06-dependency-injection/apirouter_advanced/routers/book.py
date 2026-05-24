"""6.4.4 APIRouter 高级玩法 — prefix + tags + dependencies 综合示例

把三个独立教学点融合到同一个 router 中：

1. prefix="/books"          → 所有接口自动加路径前缀，写 "/" 实际就是 "/books/"
2. tags=["书籍管理"]         → Swagger UI 把这组接口在 /docs 文档里独立分组
3. dependencies=[Depends()]  → router 级别的公共依赖，每个接口调用前都会先执行
                              (典型用途: 登录校验、限流、租户隔离)

三个特性可以独立使用，但放在一起最能体现 APIRouter "把横切关注点从路由函数里抽走" 的价值。
"""

from fastapi import APIRouter, Depends, HTTPException


# ────────────────────────────────────────────────────────────────────
# 公共依赖：登录校验 (这里简化为对比固定 token)
# ────────────────────────────────────────────────────────────────────
async def verify_token(token: str):
    """从 query string 取 token；校验失败抛 401。

    生产实际会用 OAuth2PasswordBearer 从 Authorization Header 解 JWT，
    见 ch07-auth-security/。
    """
    if token != "my-secret-token":
        raise HTTPException(status_code=401, detail="未授权的访问")
    return True


# ────────────────────────────────────────────────────────────────────
# 一次性整合三个高级特性
# ────────────────────────────────────────────────────────────────────
book_router = APIRouter(
    prefix="/books",  # 1. 所有路径自动加 /books 前缀
    tags=["书籍管理"],  # 2. 文档分组
    dependencies=[Depends(verify_token)],  # 3. 公共依赖
)


@book_router.get("/")
async def get_all_books():
    """查询所有书 — 实际访问路径: GET /books/?token=..."""
    return {
        "message": "查询成功",
        "data": [
            {"id": 1, "title": "Python 入门", "author": "张三"},
            {"id": 2, "title": "Effective Python", "author": "Brett Slatkin"},
        ],
    }


@book_router.get("/{book_id}")
async def get_book(book_id: int):
    """按 ID 查单本书"""
    return {
        "message": "查询成功",
        "data": {"id": book_id, "title": "特定书籍", "author": "李四"},
    }


@book_router.post("/")
async def create_book(title: str, author: str):
    """新增一本书 (title/author 通过 query string 传)"""
    return {
        "message": "书籍创建成功",
        "data": {"title": title, "author": author},
    }
