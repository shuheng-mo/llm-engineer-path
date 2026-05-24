"""3.2 查询参数 (Query Parameters)"""

from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/")  # 从哪开始 + 拿多少条
async def read_users(skip: int = 0, limit: int = 10, q: Union[str, None] = None):
    # URL 示例: /users/?skip=20&limit=5&q=admin
    return {"skip": skip, "limit": limit, "q": q}
