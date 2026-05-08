"""完整链 Prompt → Model → Parser — 字符串/JSON 两种输出

对应课程章节：第六章 / 5.2
"""
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# === 示例 1：基础字符串输出 ===
prompt = ChatPromptTemplate.from_template("请用100字以内介绍：{topic}")
model = ChatOpenAI(model="qwen-plus", temperature=0.7)
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({"topic": "人工智能"})
print(result)


# === 示例 2：JSON 结构化输出 ===
class BookInfo(BaseModel):
    title: str = Field(description="书名")
    author: str = Field(description="作者")
    summary: str = Field(description="内容简介")
    rating: float = Field(description="推荐指数（1-5）")


json_prompt = ChatPromptTemplate.from_template(
    """请推荐一本关于{topic}的书籍，以JSON格式输出，包含以下字段：
    - title: 书名
    - author: 作者
    - summary: 内容简介
    - rating: 推荐指数（1-5）

    只输出JSON，不要其他内容。"""
)

json_parser = JsonOutputParser(pydantic_object=BookInfo)
json_chain = json_prompt | model | json_parser

book = json_chain.invoke({"topic": "机器学习"})
print(f"书名：{book['title']}")
print(f"作者：{book['author']}")
print(f"简介：{book['summary']}")
print(f"评分：{book['rating']}")
