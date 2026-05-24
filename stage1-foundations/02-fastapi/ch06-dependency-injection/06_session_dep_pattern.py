"""6.3 数据库 Session 依赖的标准写法 (扩展自 ch05/orm/database.py)

本文件展示如何在 orm/database.py 中追加 get_session() 异步生成器，
配合下一节 07_use_session_in_route.py 注入到路由。
"""

from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession

# 修改这个 DATABASE_URL
DATABASE_URL = "sqlite+aiosqlite:///./orm/books.db"

# 其他不变 ....


# 新增这个方法
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖

    使用 yield 确保：
    1. 请求前创建 session
    2. 请求后自动关闭 session
    3. 异常时也能正确清理
    """
    async with async_session() as session:
        yield session  # 暂停执行，把session交给路由函数
        # 路由函数用完后，才会执行下面的代码（如果有的话）
