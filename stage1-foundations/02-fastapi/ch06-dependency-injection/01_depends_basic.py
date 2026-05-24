"""6.1 Depends 基本用法 — 公共查询参数依赖"""

from fastapi import Depends, FastAPI

app = FastAPI()


# 定义一个依赖项函数
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


# 在路径操作中使用依赖
@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
