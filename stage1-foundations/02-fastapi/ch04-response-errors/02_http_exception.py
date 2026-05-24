"""4.2 HTTPException 抛出 4xx 错误"""

from fastapi import FastAPI, HTTPException

items = {"foo": "The Foo Wrestlers"}

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
