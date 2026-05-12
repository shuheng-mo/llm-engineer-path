"""Handoffs — Step 3：阶段配置（每阶段的 prompt / tools / requires）

对应课程章节：模块六 / 三 / Step 3
"""
# from .02_transition_tools import (
#     record_preferences, select_destination, generate_itinerary,
#     search_flights, search_hotels, search_attractions,
# )

PREFERENCE_COLLECTOR_PROMPT = """你是旅行规划助手的第一线。

当前阶段：偏好收集

任务：
1. 热情问候用户
2. 依次询问：预算范围、旅行风格、出行日期
3. 收集完成后使用 record_preferences 记录并进入下一步

注意：友好对话，不要一次问多个问题"""

DESTINATION_RECOMMENDER_PROMPT = """你是旅行目的地推荐专家。

当前阶段：目的地推荐
用户偏好：预算 {budget_level}, 风格 {travel_style}, 日期 {travel_dates}

任务：
1. 根据偏好推荐2-3个目的地
2. 用户确认后使用 select_destination 进入下一步

可用工具：search_flights, search_hotels, search_attractions"""

ITINERARY_PLANNER_PROMPT = """你是行程规划专家。

当前阶段：行程制定
用户信息：预算 {budget_level}, 风格 {travel_style}, 日期 {travel_dates}, 目的地 {destination}

任务：
1. 使用搜索工具获取航班、酒店、景点信息
2. 制定详细行程
3. 使用 generate_itinerary 输出最终行程"""

STEP_CONFIG = {
    "preference_collector": {
        "prompt": PREFERENCE_COLLECTOR_PROMPT,
        "tools": [record_preferences],  # noqa: F821
        "requires": [],
    },
    "destination_recommender": {
        "prompt": DESTINATION_RECOMMENDER_PROMPT,
        "tools": [select_destination, search_flights, search_hotels, search_attractions],  # noqa: F821
        "requires": ["budget_level", "travel_style", "travel_dates"],
    },
    "itinerary_planner": {
        "prompt": ITINERARY_PLANNER_PROMPT,
        "tools": [generate_itinerary, search_flights, search_hotels, search_attractions],  # noqa: F821
        "requires": ["budget_level", "travel_style", "travel_dates", "destination"],
    },
}
