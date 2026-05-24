"""6.3 在路由中注入 Session

依赖 ch05-orm/orm 的 models.py 与 database.py (内含 get_session)。
"""

from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from orm.models import Book
from orm.database import get_session

app = FastAPI()


@app.post("/books/")
async def create_book_api(
    book: Book,
    # 注入 Session！
    session: AsyncSession = Depends(get_session),
):
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book
