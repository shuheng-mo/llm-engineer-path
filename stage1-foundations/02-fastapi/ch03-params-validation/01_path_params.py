"""3.1 路径参数 (Path Parameters)"""

from fastapi import FastAPI

app = FastAPI()


# 路径参数 item_id 被定义为 int 类型
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # 如果访问 /items/pig, FastAPI 会自动报错, 因为 pig 不是 int
    return {"item_id": item_id, "type": str(type(item_id))}
