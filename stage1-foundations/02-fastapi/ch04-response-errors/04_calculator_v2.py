"""4.4 实战 — 升级计算器 API (统一响应模型 + 异常处理)

在 ch03 计算器基础上引入泛型响应模型 StandardResponse[T]。
运行: uv run uvicorn 04_calculator_v2:app --reload
"""

from enum import Enum
from typing import Generic, Optional, TypeVar

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="计算器 API v2")

T = TypeVar("T")


class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalcRequest(BaseModel):
    a: float
    b: float
    op: Operation


# 1. 定义泛型响应模型
class StandardResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "Success"
    data: Optional[T] = None


# 2. 业务逻辑
@app.post("/calculate/v2", response_model=StandardResponse[float])
async def calculate_v2(request: CalcRequest):
    if request.op == Operation.divide and request.b == 0:
        # 优雅地抛出错误
        raise HTTPException(status_code=400, detail="除数不能为零")

    # ... 计算逻辑 ...
    result = ...

    # 返回对象，FastAPI 会自动填充到 StandardResponse 的结构中
    # 注意：如果手动构造 StandardResponse，则不需要 response_model 自动过滤
    return StandardResponse(data=result)
