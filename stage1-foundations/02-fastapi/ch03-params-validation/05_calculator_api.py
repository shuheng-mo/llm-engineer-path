"""3.5 实战项目 — 简易计算器 API

运行: uv run uvicorn 05_calculator_api:app --reload
"""

from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Operation(str, Enum):
    add = "+"
    subtract = "-"
    multiply = "*"
    divide = "/"


class CalcRequest(BaseModel):
    a: float
    b: float
    op: Operation


# 使用枚举限制运算符
@app.post("/calculate")
async def calculate(request: CalcRequest):
    if request.op == Operation.divide and request.b == 0:
        return {"error": "除数不能为0"}
    result = 0
    if request.op == Operation.add:
        result = request.a + request.b
    # ... 其他逻辑
    return {"result": result}
