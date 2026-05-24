"""5.2 数据模型定义 (SQLModel)"""

from typing import Optional
from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    """
    图书模型

    参数说明：
    - table=True: 标记这是一个数据库表模型
    - Field(): SQLModel 专用的字段定义工具
    """

    # 主键字段
    id: Optional[int] = Field(
        default=None,  # 新建时不需要提供，数据库自动生成
        primary_key=True,  # 标记为主键
        description="图书 ID",
    )

    # 标题字段
    title: str = Field(
        index=True,  # 创建索引，加速查询
        nullable=False,  # 不允许为空
        description="图书标题",
    )

    # 作者字段
    author: str = Field(description="作者名称")

    # 价格字段
    price: float = Field(
        gt=0,  # 大于 0
        description="图书价格",
    )

    # 描述字段（可选）
    description: Optional[str] = Field(default=None, description="图书描述")
