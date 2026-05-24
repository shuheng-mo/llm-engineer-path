"""5.5 CRUD 完整测试代码

运行: cd stage1-foundations/02-fastapi/ch05-orm && uv run pytest test_crud.py -v -s
"""

import pytest

from crud import create_book, delete_book, get_book_by_id, get_books, update_book
from orm.database import init_db
from orm.models import Book


@pytest.mark.asyncio
async def test_book_crud_operations():
    """测试 Book 模型的完整 CRUD 操作"""
    await init_db()
    print("✅ 数据库初始化完成")

    # CREATE
    print("\n--- 测试创建图书 ---")
    book_data = Book(
        title="《Python 编程指南》",
        author="Guido van Rossum",
        price=68.0,
        description="一本关于 Python 编程的权威指南",
    )
    created_book = await create_book(book_data)
    print(f"✅ 创建成功: ID={created_book.id}, 标题={created_book.title}")
    assert created_book.id is not None

    # READ all
    print("\n--- 测试查询所有图书 ---")
    books = await get_books()
    print(f"✅ 共查询到 {len(books)} 本图书")
    assert len(books) > 0

    # READ by id
    print("\n--- 测试按 ID 查询 ---")
    found_book = await get_book_by_id(created_book.id)
    print(f"✅ 查询成功: {found_book.title}")
    assert found_book is not None

    # UPDATE
    print("\n--- 测试更新图书 ---")
    update_data = Book(
        title="《Python 编程指南（第 2 版）》",
        author="Guido van Rossum",
        price=78.0,
        description="更新版的 Python 编程权威指南",
    )
    updated_book = await update_book(created_book.id, update_data)
    print(f"✅ 更新成功: 新标题={updated_book.title}, 新价格={updated_book.price}")
    assert updated_book.price == 78.0

    # DELETE
    print("\n--- 测试删除图书 ---")
    delete_result = await delete_book(created_book.id)
    assert delete_result is True
    deleted_book = await get_book_by_id(created_book.id)
    assert deleted_book is None
    print("✅ 确认图书已被删除")
    print("\n🎉 所有测试通过！")
