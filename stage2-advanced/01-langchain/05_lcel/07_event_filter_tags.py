"""事件过滤 — 用 tags 限定只看某些组件的事件

对应课程章节：第六章 / 4.5
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = os.getenv("DASHSCOPE_MODEL_NAME") or "qwen-max"

model = ChatOpenAI(api_key=api_key, base_url=base_url, model=model_name, temperature=0)
prompt = ChatPromptTemplate.from_template("请介绍：{topic}")
parser = StrOutputParser()

# 给每个组件加 tag
chain = prompt.with_config(tags=["prompt"]) | model.with_config(tags=["llm"]) | parser


async def main():
    async for event in chain.astream_events(
        {"topic": "AI"},
        version="v2",
        include_tags=["llm"],  # 只看 llm 相关的事件
    ):
        print(event)


asyncio.run(main())
