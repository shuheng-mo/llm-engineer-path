"""3.5 实战项目 — 简易计算器 API

运行: uv run uvicorn 05_calculator_api:app --reload
"""

from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# 多继承：同时继承 str 和 Enum，每个成员既是 Enum 也是 str。
# 好处：JSON 可直接序列化、可与字符串 == 比较、Pydantic/FastAPI 校验天然支持。
# 没有 str 父类的话，json.dumps(Operation.add) 会报错、Operation.add == "+" 会是 False。
# Python 3.11+ 可直接用 from enum import StrEnum 替代 (str, Enum) 混合写法。
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
    elif request.op == Operation.subtract:
        result = request.a - request.b
    elif request.op == Operation.multiply:
        result = request.a * request.b
    elif request.op == Operation.divide:
        result = request.a / request.b
    return {"result": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
