"""PydanticOutputParser — 直接解析为 Pydantic 对象

对应课程章节：第五章 / 2.3
"""

import os
from typing import List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


class MovieReview(BaseModel):
    """电影评价数据模型"""

    title: str = Field(description="电影名称")
    rating: float = Field(description="评分 (0-10)", ge=0, le=10)
    pros: List[str] = Field(description="优点列表")
    cons: List[str] = Field(description="缺点列表")
    summary: str = Field(description="一句话总结")
    recommended: bool = Field(description="是否推荐观看")


parser = PydanticOutputParser(pydantic_object=MovieReview)

print("\n格式指令")
print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专业的电影评论家，请你根据用户的描述来生成电影评价。\n {format_instructions}",
        ),
        ("human", "{movie_description}"),
    ]
)

model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
    temperature=0,
)
chain = prompt | model | parser

result = chain.invoke(
    {
        "format_instructions": parser.get_format_instructions(),
        "movie_description": "我刚看了《盗梦空间》，觉得剧情很烧脑，特效也很震撼，就是有些地方看不太懂。",
    }
)

print("\n下面是结果：")
print(f"类型： {type(result)}")
print(f"电影： {result.title}")
print(f"评分： {result.rating}")
print(f"推荐： {'是' if result.recommended else '否'}")
