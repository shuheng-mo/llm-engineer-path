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

# 显式加载 04-langgraph/.env，避免脚本从 repo 根运行时找不到
load_dotenv(Path(__file__).with_name(".env"))


@lru_cache(maxsize=None)
def get_chat_model(
    name: str = "qwen-plus",
    temperature: float | None = None,
    top_p: float | None = None,
) -> ChatTongyi:
    """按 (model, temperature, top_p) 缓存的 ChatTongyi 实例。

    同一组参数多次调用返回同一对象；不同参数组合各自缓存一份。
    `bind_tools()` 返回的是新 Runnable 不会改写缓存，可安全链式调用。

    ── 模型名约定 ──────────────────────────────────────────
    ChatTongyi 走的是「原生 DashScope 端点」(dashscope.aliyuncs.com/api/v1)，
    它只认稳定别名，**不要写带版本号的名字**：

      ✅ qwen-turbo / qwen-flash / qwen-plus / qwen-max / qwen3-max
      ❌ qwen3.5-flash / qwen3.5-plus / qwen3.6-flash / qwen3-plus
         （这些只在 OpenAI 兼容端点 /compatible-mode/v1 可用，
          Bailian console 显示的就是那边的名字，会和这里对不上）

    四个无版本号别名永远指向各档位「当前稳定最新版」，写死即可。

    ── 已知 gotcha ────────────────────────────────────────
    api_key 直接传原始字符串，让 pydantic 自动包装为 SecretStr。
    手动 SecretStr(...) 会被 pydantic v2 二次序列化成 '**********' 字面值，
    导致 dashscope 返回 401 InvalidApiKey。
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未设置 — 请在 04-langgraph/.env 中配置")
    kwargs: dict = {"model": name, "api_key": api_key}
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
