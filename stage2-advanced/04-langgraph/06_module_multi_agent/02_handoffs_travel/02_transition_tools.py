"""Handoffs — Step 2：状态转换工具（用 Command 切 current_step）

对应课程章节：模块六 / 三 / Step 2
"""
from typing import Literal

from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

# from .01_state import TravelPlanningState


@tool
def record_preferences(
    budget_level: Literal["economy", "comfort", "luxury"],
    travel_style: Literal["relaxation", "culture", "adventure"],
    travel_dates: str,
    runtime: ToolRuntime[None, "TravelPlanningState"],   # noqa: F821
) -> Command:
    """记录用户旅行偏好并转换到目的地推荐步骤"""
    return Command(update={
        "messages": [ToolMessage(
            content=f"偏好已记录 - 预算: {budget_level}, 风格: {travel_style}, 日期: {travel_dates}",
            tool_call_id=runtime.tool_call_id,
        )],
        "budget_level": budget_level,
        "travel_style": travel_style,
        "travel_dates": travel_dates,
        "current_step": "destination_recommender",
    })


@tool
def select_destination(
    destination: str,
    runtime: ToolRuntime[None, "TravelPlanningState"],   # noqa: F821
) -> Command:
    """确认目的地选择并转换到行程制定步骤"""
    return Command(update={
        "messages": [ToolMessage(
            content=f"目的地已选择: {destination}",
            tool_call_id=runtime.tool_call_id,
        )],
        "destination": destination,
        "current_step": "itinerary_planner",
    })


@tool
def generate_itinerary(itinerary: str) -> str:
    """生成最终行程安排"""
    return f"行程已生成:\n{itinerary}"


@tool
def search_flights(destination: str) -> str:
    """搜索航班信息"""
    return f"找到飞往{destination}的航班 - 直飞 ¥2580, 转机 ¥1890"


@tool
def search_hotels(destination: str) -> str:
    """搜索酒店信息"""
    return f"{destination}推荐酒店 - 五星 ¥800/晚, 四星 ¥450/晚, 民宿 ¥200/晚"


@tool
def search_attractions(destination: str) -> str:
    """搜索景点信息"""
    return f"{destination}热门景点 - 景点A, 景点B, 景点C"
