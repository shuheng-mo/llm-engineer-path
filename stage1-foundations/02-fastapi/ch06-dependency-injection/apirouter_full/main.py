"""6.4.3 完整项目结构示例 — main.py

运行: cd apirouter_full && uv run uvicorn main:app --reload
"""

from fastapi import FastAPI
from routers.book import book_router
from typing import Dict

app = FastAPI()

# 步骤3: 注册子路由
app.include_router(book_router)


@app.get("/")
async def read_root() -> Dict:
    return {"message": "欢迎来到我的图书馆！"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
