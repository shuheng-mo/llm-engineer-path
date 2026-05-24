"""6.3 在路由中注入 Session

依赖 ch05-orm/orm 的 models.py 与 database.py (内含 get_session)。

运行（在本目录下直接起即可，无需 PYTHONPATH）:
    cd stage1-foundations/02-fastapi/ch06-dependency-injection
    uv run uvicorn 07_use_session_in_route:app --reload
"""

# 把 ch05-orm/ 加入 sys.path，让 `from orm.* import ...` 跨章节工作。
# 否则 `from orm.models` 会找不到包（orm/ 不在 ch06 目录下）。
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ch05-orm"))

from fastapi import Depends, FastAPI  # noqa: E402
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: E402

from orm.database import get_session  # noqa: E402
from orm.models import Book  # noqa: E402

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
