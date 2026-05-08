"""MCP Server — 天气（streamable-http 传输 + 结构化输出）

对应课程章节：模块三 / 4.3.2
"""
from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Weather")


class WeatherData(BaseModel):
    temperature: float
    condition: str


@mcp.tool()
async def get_weather(location: str) -> str:
    """获取天气信息"""
    return f"{location} 的天气是晴天，温度 25°C"


@mcp.tool()
async def get_detailed_weather(location: str) -> WeatherData:
    """获取详细天气数据（结构化输出）"""
    return WeatherData(temperature=25.0, condition="sunny")


@mcp.resource("weather://{location}/history")
async def get_weather_history(location: str) -> str:
    """返回历史天气数据"""
    return f"{location} 过去7天天气记录..."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
