"""结构化抽取任务 — Person/Event/Time/Location 多类实体抽取

对应课程章节：第五章 / 4.3
"""
import os
from enum import Enum
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    EVENT = "event"


class Person(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None


class Event(BaseModel):
    name: str
    description: str
    participants: List[str] = Field(default_factory=list)


class TimeInfo(BaseModel):
    original: str
    normalized: Optional[str]
    is_exact: bool


class Location(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class ExtractionResult(BaseModel):
    entities: List[Person]
    events: List[Event]
    times: List[TimeInfo]
    locations: List[Location]
    confidence_score: float
    notes: Optional[str] = None


class InformationExtractor:
    def __init__(self, llm: ChatOpenAI = None):
        load_dotenv()

        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("DASHSCOPE_BASE_URL")
        if not api_key or not base_url:
            raise ValueError("API key or base URL is missing in environment variables.")

        self.llm = llm or ChatOpenAI(
            model="qwen-max", temperature=0,
            api_key=api_key, base_url=base_url,
        )
        self.structured_model = self.llm.with_structured_output(
            schema=ExtractionResult,
            method="function_calling",
            include_raw=False,
        )

    def extract(self, text: str) -> ExtractionResult:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的信息抽取系统，请严格按照以下要求输出JSON格式数据：
1. JSON字段名必须使用英文；
2. persons数组元素包含：name、role、description；
3. events数组元素包含：name、description、participants；
4. times数组元素包含：original、normalized、is_exact；
5. locations数组元素包含：name、type、description；
6. confidence_score取值范围0-1；
7. 仅输出JSON内容，不要任何额外说明。"""),
            ("human", "请从以下文本中抽取信息：\n{text}"),
        ])

        chain = prompt | self.structured_model
        return chain.invoke({"text": text})


if __name__ == "__main__":
    extractor = InformationExtractor()

    sample_text = """
    2024年3月15日，苹果公司在加州库比蒂诺总部举行了春季发布会。
    CEO 蒂姆·库克宣布推出新款 iPhone 15 Pro，售价 999 美元起。
    分析师预测这款产品将为苹果带来超过 500 亿美元的年收入。
    """

    result = extractor.extract(sample_text)
    print(result)
