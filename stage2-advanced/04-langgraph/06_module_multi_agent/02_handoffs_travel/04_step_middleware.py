"""Handoffs — Step 4：阶段中间件（动态注入 prompt + 切换工具集）

对应课程章节：模块六 / 三 / Step 4
"""

from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

# from .03_step_config import STEP_CONFIG


@wrap_model_call
def apply_step_config(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """根据 state.current_step 动态注入 prompt + 切换可用工具集。"""
    current_step = request.state.get("current_step", "preference_collector")
    step_config = STEP_CONFIG[current_step]  # noqa: F821

    # 校验前置依赖
    for key in step_config["requires"]:
        if request.state.get(key) is None:
            raise ValueError(
                f"阶段 {current_step} 需要完整状态: {key} 未设置"
                f"（当前状态: {list(request.state.keys())}）"
            )

    system_prompt = step_config["prompt"].format(**request.state)

    request = request.override(
        system_prompt=system_prompt,
        tools=step_config["tools"],
    )
    return handler(request)
