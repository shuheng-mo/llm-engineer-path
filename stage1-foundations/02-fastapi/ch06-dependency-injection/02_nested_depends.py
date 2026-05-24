"""6.2 嵌套依赖 — 依赖项本身也可以使用 Depends"""

from fastapi import Depends, Header, FastAPI

app = FastAPI()


# 第一层依赖
async def get_token(token: str = Header(...)):
    return token


# 第二层依赖（依赖于第一层）
async def get_current_user(token: str = Depends(get_token)):
    # 模拟验证 token
    user = "decode_token " + token
    return user


# 路由函数（依赖于第二层）
@app.get("/me")
async def read_current_user(user: dict = Depends(get_current_user)):
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
