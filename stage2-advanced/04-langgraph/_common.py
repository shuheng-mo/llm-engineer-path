"""04-langgraph 模块共享工具 — 模型加载等横切代码集中在这里。

为什么是单文件而不是 package：
    04-langgraph 下各子目录名以数字开头（01_module_basics ...），不是合法 Python
    package。所以我们把共享代码放在 04-langgraph 根的一个普通模块里，每个脚本
    通过 sys.path 临时注入这个目录即可 import。

用法（脚本顶部 3 行 bootstrap）：

    import sys, pathlib
    sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph")))
    from _common import get_chat_model, get_weather, get_time

    model = get_chat_model()                          # 默认 qwen-max
    model_with_tools = get_chat_model().bind_tools([get_weather, get_time])
"""

import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
from pydantic import SecretStr

# 显式加载 04-langgraph/.env，避免脚本从 repo 根运行时找不到
load_dotenv(Path(__file__).with_name(".env"))


@lru_cache(maxsize=None)
def get_chat_model(
    name: str = "qwen-max",
    temperature: float | None = None,
    top_p: float | None = None,
) -> ChatTongyi:
    """按 (model, temperature, top_p) 缓存的 ChatTongyi 实例。

    同一组参数多次调用返回同一对象；不同参数组合各自缓存一份。
    `bind_tools()` 返回的是新 Runnable 不会改写缓存，可安全链式调用。
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未设置 — 请在 04-langgraph/.env 中配置")
    kwargs: dict = {"model": name, "api_key": SecretStr(api_key)}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    return ChatTongyi(**kwargs)


# ============================================================
# 共享 demo tools — 在多个示例中反复出现的占位工具
# ============================================================


@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天，25°C"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
