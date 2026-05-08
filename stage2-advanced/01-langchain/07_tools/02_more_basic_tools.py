"""更多基础 Tool 示例 — 时间/乘法/天气

对应课程章节：第八章 / 2.1.3
"""
from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def multiply(a: float, b: float) -> float:
    """将两个数字相乘。"""
    return a * b


@tool
def search_weather(city: str) -> str:
    """查询指定城市的天气信息。"""
    weather_data = {
        "北京": "晴天，温度 25°C，湿度 40%",
        "上海": "多云，温度 28°C，湿度 65%",
        "广州": "小雨，温度 30°C，湿度 80%",
    }
    return weather_data.get(city, f"抱歉，未找到 {city} 的天气信息")
