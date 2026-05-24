"""4.1 响应模型 (response_model)

UserOut 中未定义 password 字段，FastAPI 会自动从响应中过滤掉。
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: str


class UserOut(BaseModel):
    username: str
    email: str


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    # 即使这里返回了包含 password 的对象，响应中也只会保留 UserOut 声明的字段
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
