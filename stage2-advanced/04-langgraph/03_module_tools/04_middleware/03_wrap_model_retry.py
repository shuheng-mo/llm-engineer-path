"""Middleware — Wrap-style Hook 实现重试机制

对应课程章节：模块三 / 3.3.3
"""
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call


@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"重试 {attempt + 1}/3: {e}")


agent = create_agent(
    model=model,                # noqa: F821
    tools=tools,                # noqa: F821
    middleware=[retry_model],
)
