"""astream_events — 看链上每个事件（chain_start / model_stream / chain_end）

对应课程章节：第六章 / 4.3
"""

import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


async def demo_astream_events():
    prompt = ChatPromptTemplate.from_template("请介绍：{topic}")
    model = ChatOpenAI(model="gpt-4.1")
    parser = StrOutputParser()
    chain = prompt | model | parser

    async for event in chain.astream_events({"topic": "量子计算"}, version="v2"):
        kind = event["event"]
        name = event.get("name", "")

        if kind == "on_chain_start":
            print(f"🚀 开始执行: {name}")
        elif kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)
        elif kind == "on_chain_end":
            print(f"\n✅ 执行完成: {name}")


if __name__ == "__main__":
    asyncio.run(demo_astream_events())
