"""Handoffs — 3.5 添加回退功能（go_back_to_preferences / destination）

对应课程章节：模块六 / 三 / 3.5
"""

from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

# from .01_state import TravelPlanningState


@tool
def go_back_to_preferences(runtime: ToolRuntime[None, "TravelPlanningState"]) -> Command:  # noqa: F821
    """返回到偏好收集步骤"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="已重置状态，请重新提供偏好信息。", tool_call_id=runtime.tool_call_id
                )
            ],
            "current_step": "preference_collector",
        }
    )


@tool
def go_back_to_destination(runtime: ToolRuntime[None, "TravelPlanningState"]) -> Command:  # noqa: F821
    """返回到目的地推荐步骤"""
    return Command(
        update={
            "messages": [
                ToolMessage(content="已返回目的地推荐阶段。", tool_call_id=runtime.tool_call_id)
            ],
            "current_step": "destination_recommender",
        }
    )


# 加完后需要更新 STEP_CONFIG 和 all_tools，并更新 ITINERARY_PLANNER_PROMPT 让 LLM 知道这俩工具：
# STEP_CONFIG["itinerary_planner"]["tools"].extend([go_back_to_preferences, go_back_to_destination])
