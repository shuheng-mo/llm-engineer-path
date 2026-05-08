"""JsonOutputParser — JSON 解析（无 Schema / 带 Pydantic Schema）

对应课程章节：第五章 / 2.2
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


# === 1. 不带 Schema ===
parser = JsonOutputParser()
print("自动生成的格式指令：")
print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的信息提取助手，请你根据要求输出内容： {format_instructions}"),
    ("human", "从以下文本信息中提取出人物信息： {text}"),
])

model = init_chat_model(
    model="qwen-max", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0,
)

chain = prompt | model | parser
result = chain.invoke({
    "format_instructions": parser.get_format_instructions(),
    "text": "张三是一位 25 岁软件工程师，在北京工作",
})
print(f"\n返回类型： {type(result)}")
print(result)


# === 2. 带 Pydantic Schema ===
class PersonInfo(BaseModel):
    name: str = Field(description="人物姓名")
    age: str = Field(description="人物年龄")
    occupation: str = Field(description="人物职业")
    location: str = Field(description="所在城市")


parser = JsonOutputParser(pydantic_object=PersonInfo)

print("\n下面是带有 Schema 的指令：")
print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个信息提取助手。{format_instructions}"),
    ("human", "从以下文本中提取人物信息：{text}"),
])

model = init_chat_model(
    model="qwen-plus", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0,
)

chain = prompt | model | parser
result = chain.invoke({
    "format_instructions": parser.get_format_instructions(),
    "text": "张三是一位 35 岁的软件工程师，在北京工作。",
})
print("\n最终格式化的数据：")
print(result)
