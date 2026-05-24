"""5.3 数据库连接与异步 Session 配置

DATABASE_URL 两种常见形式 (见 block 21):
    mysql+aiomysql://root:pwd@localhost:3306/books_db?charset=utf8mb4
    sqlite+aiosqlite:///./books.db
本示例使用 SQLite (无需安装数据库服务)。
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

# 数据库连接 URL
# sqlite+aiosqlite:/// 表示使用异步 SQLite 驱动
DATABASE_URL = "sqlite+aiosqlite:///./books.db"

# 1. 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 打印 SQL 语句（开发时有用，生产环境建议关闭）
    future=True,  # 启用 SQLAlchemy 2.0 特性
)
# 2. 创建异步 Session 工厂
# expire_on_commit=False: 提交后对象仍然可用
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,  # 指定会话类型为异步会话（同步会话是 Session），必须与异步引擎匹配。
    # 默认情况下，会话提交（commit）后，查询出来的对象会 “过期”（无法再访问属性），
    # 设为 False 后，提交后对象仍可正常使用（开发更友好）
    expire_on_commit=False,  #
)


# 3. 初始化数据库表结构
async def init_db():
    """
    创建所有表
    这个函数应该在应用启动时调用一次
    """
    # 通过异步引擎开启一个事务连接（engine.begin() 会自动管理事务，退出上下文时提交），
    # conn 是数据库连接实例。
    async with engine.begin() as conn:
        # 如果需要重建表，可以先删除
        # await conn.run_sync(SQLModel.metadata.drop_all)

        # 创建所有表（如果不存在）
        await conn.run_sync(SQLModel.metadata.create_all)
