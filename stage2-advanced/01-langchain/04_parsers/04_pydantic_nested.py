"""Pydantic 复杂嵌套结构 — Address / Education / PersonProfile

对应课程章节：第五章 / 2.3 复杂嵌套
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()


class Address(BaseModel):
    city: str = Field(description="城市")
    district: str = Field(description="区/县")
    street: Optional[str] = Field(default=None, description="街道")


class Education(BaseModel):
    school: str = Field(description="学校名称")
    degree: str = Field(description="学位")
    major: str = Field(description="专业")
    graduation_year: int = Field(description="毕业年份")


class PersonProfile(BaseModel):
    name: str
    age: int
    gender: str
    address: Address
    education: List[Education]
    skills: List[str]
    bio: str


parser = PydanticOutputParser(pydantic_object=PersonProfile)
print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个信息抽取专家，请严格按照要求输出。\n{format_instructions}"),
        ("human", "请根据以下文本生成完整人物档案：\n{text}"),
    ]
)

model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)

chain = prompt | model | parser

text = """
张三，男，28岁，目前居住在北京市朝阳区。
毕业于清华大学计算机科学专业，本科毕业于2020年。
后来在北京大学获得硕士学位，2023年毕业。
擅长Python、Java和机器学习。
他是一名热爱技术的软件工程师，喜欢开源和分享。
"""

result = chain.invoke(
    {
        "format_instructions": parser.get_format_instructions(),
        "text": text,
    }
)

print(type(result))
print(result)
print(result.name, result.address.city, result.education[0].school)
