"""@tool 装饰器最基础用法

对应课程章节：模块三 / 1.1.2
"""

from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。

    Args:
        city: 城市名称，例如"北京"、"上海"

    Returns:
        天气信息描述字符串
    """
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "深圳": "雷阵雨，30°C",
    }
    return weather_data.get(city, f"{city}的天气信息暂时无法获取")


if __name__ == "__main__":
    print(get_weather.name)  # get_weather
    print(get_weather.description)  # 获取指定城市的天气信息...
    result = get_weather.invoke({"city": "北京"})
    print(result)  # 晴天，25°C
