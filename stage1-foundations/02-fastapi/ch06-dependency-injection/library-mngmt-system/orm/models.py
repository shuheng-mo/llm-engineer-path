"""Book 数据模型

table=True  → 告诉 SQLModel 这个类对应一张真实的数据库表
SQLModel    → 同时具备 Pydantic 数据验证 和 SQLAlchemy ORM 两种能力

⚠️ SQLModel 已知 quirk:
   带 `table=True` 的类实例化时会跳过 Pydantic 校验 (gt/lt/max_length 等约束不强制),
   只在 OpenAPI 文档里展示约束信息。这是 SQLAlchemy 的设计妥协 (需要能从 row 直接重建)。
   生产代码若需要严格校验请求体，应拆成两个模型：
     - BookCreate(SQLModel)         # 不带 table=True, 走完整 Pydantic 校验
     - Book(SQLModel, table=True)   # 数据库表模型
   路由签名用 BookCreate 接请求 → service 内部转成 Book(...) 存库。
   本课程项目保持与教学文档一致，沿用单一 Book 模型；故意传 price=0 会被接受。
"""

from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
    """图书数据库模型 — 每个字段映射成数据库表的一列"""

    # ---------- 主键 ----------
    id: Optional[int] = Field(
        default=None,  # 新建时不传，数据库自动生成
        primary_key=True,
        description="图书唯一 ID（自增主键）",
    )

    # ---------- 书名 ----------
    title: str = Field(
        index=True,  # 创建索引，让模糊搜索更快
        nullable=False,
        max_length=200,
        description="图书标题",
    )

    # ---------- 作者 ----------
    author: str = Field(
        nullable=False,
        max_length=100,
        description="作者姓名",
    )

    # ---------- 出版日期 ----------
    publish_date: Optional[date] = Field(
        default=None,
        description="出版日期，格式 YYYY-MM-DD",
    )

    # ---------- 价格 ----------
    price: float = Field(
        gt=0,  # 必须大于 0（Pydantic 验证）
        description="图书定价（元），必须 > 0",
    )

    # ---------- 简介（可选）----------
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="图书简介",
    )
