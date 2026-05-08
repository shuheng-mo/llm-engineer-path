"""Handoffs — Step 5：创建带 state_schema + middleware 的 travel_agent

对应课程章节：模块六 / 三 / Step 5
"""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langgraph.checkpoint.memory import InMemorySaver

# from .01_state import TravelPlanningState
# from .02_transition_tools import (
#     record_preferences, select_destination, generate_itinerary,
#     search_flights, search_hotels, search_attractions,
# )
# from .04_step_middleware import apply_step_config

load_dotenv()

model = ChatTongyi(model="qwen-max", api_key=os.getenv("DASHSCOPE_API_KEY"))

all_tools = [
    record_preferences, select_destination, generate_itinerary,         # noqa: F821
    search_flights, search_hotels, search_attractions,                  # noqa: F821
]

travel_agent = create_agent(
    model,
    tools=all_tools,
    state_schema=TravelPlanningState,                                   # noqa: F821
    middleware=[apply_step_config],                                     # noqa: F821
    checkpointer=InMemorySaver(),
)
