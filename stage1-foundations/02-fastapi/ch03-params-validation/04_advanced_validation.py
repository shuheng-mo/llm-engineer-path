"""3.4 进阶参数验证 (Query / Path / Field)"""

from fastapi import Query, Path, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class CalculatorInput(BaseModel):
    # Field 用于模型内部校验：必须大于 0，且小于 10000
    num_a: float = Field(..., gt=0, lt=10000, description="第一个数字")
    num_b: float = Field(..., description="第二个数字")


@app.get("/items/{item_id}")
async def read_items(
    # Path 用于路径参数校验：必须大于等于 1
    item_id: int = Path(..., ge=1, title="The ID of the item"),
    # Query 用于查询参数校验：限制最大长度为 50
    q: str | None = Query(None, max_length=50),
):
    return {"item_id": item_id, "q": q}
