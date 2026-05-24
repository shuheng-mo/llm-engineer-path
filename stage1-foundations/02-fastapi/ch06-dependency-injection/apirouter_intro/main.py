"""6.4 APIRouter 三步骤 — 步骤 3: 注册子路由到主应用

运行: cd apirouter_intro && uv run uvicorn main:app --reload
"""

# main.py (主应用文件)
from fastapi import FastAPI

# 从我们定义的路由模块中导入子路由
from routers.book import book_router  # 假设子路由写在 routers/book.py 文件中
from typing import Dict

# 1. 创建主应用实例（图书馆管理员）
app = FastAPI()

# 2. 将子路由（书籍书架）注册到主应用中
# 这一步告诉管理员：“我有一个管理书籍的书架，请把它加入图书馆！”
app.include_router(book_router)


# 主应用也可以有自己的根路径接口
@app.get("/")
async def read_root():
    return {"message": "欢迎来到我的图书馆！"}


# 运行服务器
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
