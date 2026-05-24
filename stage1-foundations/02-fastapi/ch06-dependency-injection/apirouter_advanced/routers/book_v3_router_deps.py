"""6.4.4 高级玩法 — 在路由级别添加公共依赖 (登录校验)"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException


# 模拟一个登录验证依赖
async def verify_token(token: str):
    if token != "my-secret-token":
        raise HTTPException(status_code=401, detail="未授权的访问")
    return True


# 为整个书籍路由模块添加公共依赖：所有接口都需要验证token
book_router = APIRouter(
    prefix="/books",
    tags=["书籍管理"],
    dependencies=[Depends(verify_token)],  # 所有接口都会先执行这个依赖
)


@book_router.get("/")
async def get_all_books():
    # 这个接口会自动应用 verify_token 依赖
    return {"message": "查询成功", "data": []}
