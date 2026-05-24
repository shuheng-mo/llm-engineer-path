"""6.4.4 主应用 — 挂载 apirouter_advanced 的综合 router

运行:
    cd stage1-foundations/02-fastapi/ch06-dependency-injection/apirouter_advanced
    uv run uvicorn main:app --reload

文档: http://127.0.0.1:8000/docs

测试三个特性的效果:

# ① 路径前缀生效 — 访问的是 /books/ 而不是 /
curl "http://127.0.0.1:8000/books/?token=my-secret-token"

# ② Swagger UI 里 "书籍管理" 标签下能看到这组接口 (tags 效果)
open http://127.0.0.1:8000/docs

# ③ 公共依赖生效 — 不带 token 直接 422
curl "http://127.0.0.1:8000/books/"
# 带错的 token 401
curl "http://127.0.0.1:8000/books/?token=wrong"
# 带对的 token 才能拿到数据
curl "http://127.0.0.1:8000/books/?token=my-secret-token"
"""

from fastapi import FastAPI

from routers.book import book_router

app = FastAPI(title="APIRouter 高级玩法演示")

# 把综合 router 挂到主应用上 (prefix/tags/dependencies 已经在 router 内配置好)
app.include_router(book_router)


@app.get("/", tags=["首页"])
async def root():
    return {
        "message": "访问 /docs 查看 Swagger UI",
        "hint": "所有 /books/* 接口需要 ?token=my-secret-token",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
