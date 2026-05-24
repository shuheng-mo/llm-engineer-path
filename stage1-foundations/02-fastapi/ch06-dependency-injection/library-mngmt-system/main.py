"""主应用入口

职责：
  1. 创建 FastAPI 实例
  2. 注册生命周期事件 (启动时自动建表)
  3. 挂载子路由
  4. 提供根路径欢迎接口

运行 (在本目录下):
    uv run uvicorn main:app --reload
或者：
    uv run python main.py

文档:
    http://127.0.0.1:8000/docs   (Swagger)
    http://127.0.0.1:8000/redoc  (ReDoc)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from orm.database import init_db
from routers.books import book_router


# ── 生命周期管理 (lifespan) ────────────────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """FastAPI 会在应用启动时执行 yield 之前的代码，关闭时执行 yield 之后。"""
    print("🚀 应用启动中...")
    await init_db()  # 自动检测并创建数据库表 (幂等，表已存在则跳过)
    print("✅ 数据库表初始化完成，服务已就绪！")

    yield  # ← 应用正常运行 (处理 HTTP 请求)

    print("👋 应用正在关闭，资源已释放。")


# ── 创建 FastAPI 实例 ───────────────────────────────────────────
app = FastAPI(
    title="图书管理 API",
    description="基于 FastAPI + SQLModel + aiosqlite 的图书 CRUD 接口",
    version="1.0.0",
    lifespan=lifespan,  # 绑定生命周期管理器
)


# ── 挂载子路由 ──────────────────────────────────────────────────
# include_router 把 book_router 里的所有接口注册到主应用
# book_router 的 prefix="/books" 在此生效
app.include_router(book_router)


# ── 根路径 ──────────────────────────────────────────────────────
@app.get("/", tags=["根路径"])
async def root():
    return {
        "message": "欢迎使用图书管理 API 📚",
        "docs": "访问 /docs 查看完整接口文档",
        "version": "1.0.0",
    }


# ── 直接运行入口 ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    # reload=True → 代码修改后自动重启 (开发模式)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
