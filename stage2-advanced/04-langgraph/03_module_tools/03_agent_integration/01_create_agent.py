"""create_agent 标准实现（最简版本）

对应课程章节：模块三 / 2.1.3
"""

import pathlib
import sys

from langchain.agents import create_agent

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model, get_time, get_weather  # noqa: E402

model = get_chat_model("qwen-max")

agent = create_agent(
    model=model,
    tools=[get_weather, get_time],
    system_prompt="你是一个友好的助手，可以查询天气和时间。",
)


if __name__ == "__main__":
    result = agent.invoke({"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]})
    print(result["messages"][-1].content)
