"""Handoffs — 完整 demo：端到端可运行的旅行规划助手

把 01~07 各步骤串成一个可独立运行的脚本：

  Step 1  自定义 TravelPlanningState              (对应 01_state.py)
  Step 2  Command 状态转换工具 + 业务搜索工具      (对应 02_transition_tools.py)
  Step 3  阶段配置 STEP_CONFIG                     (对应 03_step_config.py)
  Step 4  动态注入 prompt+tools 的中间件           (对应 04_step_middleware.py)
  Step 5  组装带 state_schema + middleware 的 agent (对应 05_create_agent.py)
  Step 6  4 轮线性对话                             (对应 06_run_workflow.py)
  Step 7  回退到上一步的 go_back_* 工具            (对应 07_go_back_tools.py)

运行：
    uv run python stage2-advanced/04-langgraph/06_module_multi_agent/02_handoffs_travel/08_full_demo.py
    uv run python .../08_full_demo.py --demo linear     # 仅跑 4 轮线性流程
    uv run python .../08_full_demo.py --demo go_back    # 在行程阶段触发回退
"""

import pathlib
import sys
import uuid
from typing import Callable, Literal

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import SystemMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from typing_extensions import NotRequired

sys.path.insert(
    0,
    str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")),
)
from _common import get_chat_model  # noqa: E402

# ============================================================
# Step 1：自定义状态
# ============================================================
PlanningStep = Literal["preference_collector", "destination_recommender", "itinerary_planner"]


class TravelPlanningState(AgentState):
    """旅行规划工作流状态。"""

    current_step: NotRequired[PlanningStep]
    budget_level: NotRequired[Literal["economy", "comfort", "luxury"]]
    travel_style: NotRequired[Literal["relaxation", "culture", "adventure"]]
    destination: NotRequired[str]
    travel_dates: NotRequired[str]


# ============================================================
# Step 2：状态转换工具 + 业务搜索工具
# ============================================================
@tool
def record_preferences(
    budget_level: Literal["economy", "comfort", "luxury"],
    travel_style: Literal["relaxation", "culture", "adventure"],
    travel_dates: str,
    runtime: ToolRuntime[None, TravelPlanningState],
) -> Command:
    """记录用户旅行偏好并转换到目的地推荐步骤。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"偏好已记录 - 预算: {budget_level}, 风格: {travel_style}, 日期: {travel_dates}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "budget_level": budget_level,
            "travel_style": travel_style,
            "travel_dates": travel_dates,
            "current_step": "destination_recommender",
        }
    )


@tool
def select_destination(
    destination: str,
    runtime: ToolRuntime[None, TravelPlanningState],
) -> Command:
    """确认目的地选择并转换到行程制定步骤。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"目的地已选择: {destination}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "destination": destination,
            "current_step": "itinerary_planner",
        }
    )


@tool
def generate_itinerary(itinerary: str) -> str:
    """生成最终行程安排。"""
    return f"行程已生成:\n{itinerary}"


@tool
def search_flights(destination: str) -> str:
    """搜索航班信息。"""
    return f"找到飞往{destination}的航班 - 直飞 ¥2580, 转机 ¥1890"


@tool
def search_hotels(destination: str) -> str:
    """搜索酒店信息。"""
    return f"{destination}推荐酒店 - 五星 ¥800/晚, 四星 ¥450/晚, 民宿 ¥200/晚"


@tool
def search_attractions(destination: str) -> str:
    """搜索景点信息。"""
    return f"{destination}热门景点 - 景点A, 景点B, 景点C"


# Step 7：回退工具（让 itinerary_planner 阶段允许跳回上两步）
@tool
def go_back_to_preferences(runtime: ToolRuntime[None, TravelPlanningState]) -> Command:
    """返回到偏好收集步骤（同时清空偏好以便重新收集）。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="已重置状态，请重新提供偏好信息。",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "current_step": "preference_collector",
        }
    )


@tool
def go_back_to_destination(runtime: ToolRuntime[None, TravelPlanningState]) -> Command:
    """返回到目的地推荐步骤。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="已返回目的地推荐阶段。",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "current_step": "destination_recommender",
        }
    )


# ============================================================
# Step 3：阶段配置
# ============================================================
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
1. 根据偏好推荐 2-3 个目的地
2. 用户确认后使用 select_destination 进入下一步

可用工具：search_flights, search_hotels, search_attractions"""

ITINERARY_PLANNER_PROMPT = """你是行程规划专家。

当前阶段：行程制定
用户信息：预算 {budget_level}, 风格 {travel_style}, 日期 {travel_dates}, 目的地 {destination}

任务：
1. 使用 search_flights / search_hotels / search_attractions 获取信息
2. 制定详细行程
3. 使用 generate_itinerary 输出最终行程

如果用户表示不满意，可以：
- 调用 go_back_to_destination 回到目的地推荐阶段
- 调用 go_back_to_preferences 回到偏好收集阶段（会清空之前的选择）"""


STEP_CONFIG: dict[PlanningStep, dict] = {
    "preference_collector": {
        "prompt": PREFERENCE_COLLECTOR_PROMPT,
        "tools": [record_preferences],
        "requires": [],
    },
    "destination_recommender": {
        "prompt": DESTINATION_RECOMMENDER_PROMPT,
        "tools": [
            select_destination,
            search_flights,
            search_hotels,
            search_attractions,
        ],
        "requires": ["budget_level", "travel_style", "travel_dates"],
    },
    "itinerary_planner": {
        "prompt": ITINERARY_PLANNER_PROMPT,
        "tools": [
            generate_itinerary,
            search_flights,
            search_hotels,
            search_attractions,
            go_back_to_destination,
            go_back_to_preferences,
        ],
        "requires": ["budget_level", "travel_style", "travel_dates", "destination"],
    },
}


# ============================================================
# Step 4：阶段中间件 — 动态注入 prompt + 切换工具集
# ============================================================
@wrap_model_call
def apply_step_config(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """根据 state.current_step 切换 system_prompt 与可用 tools。

    - 默认从 preference_collector 起步
    - 校验该阶段依赖的状态键齐全，否则提前抛错而不是让 LLM 看到 KeyError
    """
    current_step: PlanningStep = request.state.get("current_step", "preference_collector")
    step_config = STEP_CONFIG[current_step]

    for key in step_config["requires"]:
        if request.state.get(key) is None:
            raise ValueError(
                f"阶段 {current_step} 需要 {key}，"
                f"当前状态键: {sorted(k for k in request.state if not k.startswith('__'))}"
            )

    rendered_prompt = step_config["prompt"].format(**request.state)
    request = request.override(
        system_message=SystemMessage(content=rendered_prompt),
        tools=step_config["tools"],
    )
    return handler(request)


# ============================================================
# Step 5：组装 travel_agent
#   注意：tools 这里要列出所有可能用到的工具的「并集」，否则 override 切到
#   某阶段的子集时会找不到 tool 实现（agent 内部用 name → tool 查找）。
# ============================================================
ALL_TOOLS = [
    record_preferences,
    select_destination,
    generate_itinerary,
    search_flights,
    search_hotels,
    search_attractions,
    go_back_to_preferences,
    go_back_to_destination,
]

travel_agent = create_agent(
    get_chat_model("qwen-max"),
    tools=ALL_TOOLS,
    state_schema=TravelPlanningState,
    middleware=[apply_step_config],
    checkpointer=InMemorySaver(),
)


# ============================================================
# Step 6/7：演示
# ============================================================
def _new_config() -> RunnableConfig:
    return {"configurable": {"thread_id": f"travel_{uuid.uuid4().hex[:8]}"}}


def _turn(user_msg: str, config: RunnableConfig, label: str) -> None:
    print(f"\n=== {label} ===")
    print(f"用户 > {user_msg}")
    result = travel_agent.invoke({"messages": [{"role": "user", "content": user_msg}]}, config)
    state_snapshot = {
        k: result.get(k)
        for k in (
            "current_step",
            "budget_level",
            "travel_style",
            "travel_dates",
            "destination",
        )
        if result.get(k) is not None
    }
    print(f"助手 > {result['messages'][-1].content}")
    print(f"[state] {state_snapshot}")


def demo_linear() -> None:
    """4 轮线性流程：偏好 → 目的地 → 行程。"""
    print("\n########## Demo: 线性 4 轮规划 ##########")
    config = _new_config()
    _turn("我想规划一次旅行", config, "第1轮 (preference_collector)")
    _turn(
        "预算中等舒适型，想体验文化，7月初出发玩5天",
        config,
        "第2轮 (record_preferences → destination_recommender)",
    )
    _turn("我选择去西安", config, "第3轮 (select_destination → itinerary_planner)")
    _turn("帮我制定详细行程", config, "第4轮 (generate_itinerary)")


def demo_go_back() -> None:
    """走到行程阶段后让用户改主意，触发 go_back_to_destination。"""
    print("\n########## Demo: 触发 go_back_to_destination ##########")
    config = _new_config()
    _turn("我想规划一次旅行", config, "第1轮")
    _turn("经济型预算，想休闲度假，6月中下旬玩4天", config, "第2轮")
    _turn("先选去三亚吧", config, "第3轮")
    _turn(
        "等等，三亚我去过了，能换个地方推荐吗？",
        config,
        "第4轮 (期望: go_back_to_destination)",
    )
    _turn("那就改去厦门吧", config, "第5轮 (重新 select_destination)")
    _turn("好的，帮我出详细行程", config, "第6轮 (generate_itinerary)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Handoffs 旅行助手端到端 demo")
    parser.add_argument(
        "--demo",
        choices=["linear", "go_back", "all"],
        default="linear",
        help="选择运行哪个 demo（默认 linear；go_back 演示回退；all 顺序跑两个）",
    )
    args = parser.parse_args()
    if args.demo in ("linear", "all"):
        demo_linear()
    if args.demo in ("go_back", "all"):
        demo_go_back()
