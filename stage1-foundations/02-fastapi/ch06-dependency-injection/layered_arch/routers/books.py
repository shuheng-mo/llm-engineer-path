"""6.5 企业级架构分层 — Router 层 (片段)

需要补充: from fastapi import APIRouter, Depends; from .. import book_crud
router = APIRouter()
"""


@router.post("/", response_model=Book)
async def create_book_endpoint(book: Book, session: AsyncSession = Depends(get_session)):
    # 路由只负责“指挥”
    return await book_crud.create_book(session, book)
