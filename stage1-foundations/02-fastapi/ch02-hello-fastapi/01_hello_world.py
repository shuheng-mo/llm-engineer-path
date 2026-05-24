"""2.3 最简 FastAPI 应用 — Hello World

运行: uv run uvicorn 01_hello_world:app --reload
文档: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

# 1. 实例化 FastAPI 对象
app = FastAPI()


# 2. 路径操作装饰器
# 含义：当客户端以 GET 方法访问根路径 "/" 时，运行下方的函数
@app.get("/")
async def read_root() -> dict:
    # 3. 路径操作函数
    # 直接返回字典，FastAPI 会自动转换为 JSON
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
