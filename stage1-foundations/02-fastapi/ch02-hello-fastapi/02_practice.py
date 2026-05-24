"""2.6 实战练习 — 多路由 + 路径参数 + 文档体验

运行: uv run uvicorn 02_practice:app --reload
文档: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

app = FastAPI()


# 1. 根路径
@app.get("/")
async def read_root() -> dict:
    return {"message": "Hello World"}


# 2. /info 路由 — 返回个人信息
@app.get("/info")
def get_info() -> dict:
    return {
        "name": "Your Name",
        "role": "Student",
        "language": "Python 3.10",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
