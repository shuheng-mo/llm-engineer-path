"""6.3 yield 依赖在 FastAPI 中的用法"""

from fastapi import FastAPI, Depends
from typing import AsyncGenerator

app = FastAPI()


# 异步生成器依赖（FastAPI自动调__anext__()）
async def get_async_session() -> AsyncGenerator[str, None]:
    print("1. 创建异步数据库会话（给资源）")
    session = "异步Session对象"
    yield session  # 只需要写：给什么资源
    print("2. 关闭异步数据库会话（清资源）")  # 只需要写：怎么清


# 路由函数：注入依赖，直接用资源
@app.get("/test")
async def test(session: str = Depends(get_async_session)):
    print(f"路由：用{session}处理业务")
    return {"msg": "处理完成", "session": session}  # return → 直接结束生成器，啥也不做，啥也不打印


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
