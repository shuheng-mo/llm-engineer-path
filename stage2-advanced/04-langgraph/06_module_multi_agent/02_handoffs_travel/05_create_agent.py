"""Handoffs — Step 5：创建带 state_schema + middleware 的 travel_agent

对应课程章节：模块六 / 三 / Step 5
"""

import pathlib
import sys

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# from .01_state import TravelPlanningState
# from .02_transition_tools import (
#     record_preferences, select_destination, generate_itinerary,
#     search_flights, search_hotels, search_attractions,
# )
# from .04_step_middleware import apply_step_config

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")

all_tools = [
    record_preferences,
    select_destination,
    generate_itinerary,  # noqa: F821
    search_flights,
    search_hotels,
    search_attractions,  # noqa: F821
]

travel_agent = create_agent(
    model,
    tools=all_tools,
    state_schema=TravelPlanningState,  # noqa: F821
    middleware=[apply_step_config],  # noqa: F821
    checkpointer=InMemorySaver(),
)
