"""create_agent 标准实现（最简版本）

对应课程章节：模块三 / 2.1.3
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi

load_dotenv()

model = ChatTongyi(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)


@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天，25°C"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


agent = create_agent(
    model=model,
    tools=[get_weather, get_time],
    system_prompt="你是一个友好的助手，可以查询天气和时间。",
)


if __name__ == "__main__":
    result = agent.invoke({"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]})
    print(result["messages"][-1].content)
