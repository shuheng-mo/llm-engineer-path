"""Handoffs — Step 1：自定义 TravelPlanningState 状态

对应课程章节：模块六 / 三 / Step 1
"""

from typing import Literal

from langchain.agents import AgentState
from typing_extensions import NotRequired

PlanningStep = Literal["preference_collector", "destination_recommender", "itinerary_planner"]


class TravelPlanningState(AgentState):
    """旅行规划工作流状态"""

    current_step: NotRequired[PlanningStep]
    budget_level: NotRequired[Literal["economy", "comfort", "luxury"]]
    travel_style: NotRequired[Literal["relaxation", "culture", "adventure"]]
    destination: NotRequired[str]
    travel_dates: NotRequired[str]
