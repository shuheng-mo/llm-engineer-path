"""复杂参数：用 Pydantic 模型作 args_schema

对应课程章节：模块三 / 1.1.4
"""
from datetime import date
from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field


class FlightSearchParams(BaseModel):
    """航班搜索参数"""

    departure_city: str = Field(description="出发城市，例如'北京'")
    arrival_city: str = Field(description="到达城市，例如'上海'")
    departure_date: date = Field(description="出发日期，格式 YYYY-MM-DD")
    return_date: Optional[date] = Field(None, description="返程日期（往返票时必填）")
    passengers: int = Field(default=1, ge=1, le=9, description="乘客人数，1-9人")
    cabin_class: str = Field(default="economy", description="舱位等级：economy/business/first")


@tool(args_schema=FlightSearchParams)
def search_flights(
    departure_city: str,
    arrival_city: str,
    departure_date: date,
    return_date: Optional[date] = None,
    passengers: int = 1,
    cabin_class: str = "economy",
) -> str:
    """搜索航班信息。

    Returns:
        JSON 格式的航班列表
    """
    flight_info = {
        "route": f"{departure_city} -> {arrival_city}",
        "date": str(departure_date),
        "passengers": passengers,
        "class": cabin_class,
    }
    return f"找到 3 班符合条件的航班: {flight_info}"
