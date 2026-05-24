"""4.3 自定义全局异常处理器"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# 1. 初始化 FastAPI 应用
app = FastAPI()


# 2. 注册你写的异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    自定义 HTTP 异常处理：统一返回格式
    - code: HTTP 状态码
    - message: 异常详情
    - data: 固定为 None（也可根据需求自定义）
    """
    return JSONResponse(
        status_code=exc.status_code,  # 保持原异常的 HTTP 状态码
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


# 3. 示例接口：主动抛出 HTTPException
@app.get("/items/{item_id}", summary="根据 ID 获取商品")
async def read_item(item_id: int):
    """
    示例场景：
    - 如果 item_id 小于 1，抛出 400 异常（参数错误）
    - 如果 item_id 等于 999，抛出 404 异常（资源不存在）
    - 否则返回正常数据
    """
    if item_id < 1:
        # 主动抛出 HTTPException，会被上面的处理器捕获
        raise HTTPException(status_code=400, detail="商品 ID 不能小于 1")
    if item_id == 999:
        raise HTTPException(status_code=404, detail=f"未找到 ID 为 {item_id} 的商品")
    # 正常响应（也可以自定义格式，和异常格式统一）
    return {
        "code": 200,
        "message": "success",
        "data": {"item_id": item_id, "name": "测试商品", "price": 99.9},
    }


# 4. 启动入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
