"""从对话中自动抽取用户偏好 — JsonOutputParser + Pydantic

对应课程章节：第七章 / 5.3
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# from .09_user_profile_pydantic import UserProfile
# from .10_redis_profile_store import RedisUserProfileStore

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)


class ExtractedInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="用户名称")
    occupation: Optional[str] = Field(default=None, description="用户职业")
    skills: list[str] = Field(default_factory=list, description="用户技能")
    project: Optional[str] = Field(default=None, description="当前项目")
    preferences: Optional[dict] = Field(default_factory=dict, description="用户偏好")
    has_new_info: bool = Field(default=False, description="是否包含新信息")


extract_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个信息抽取专家。请从用户的对话中提取以下信息：
- name: 用户的名字
- occupation: 用户的职业
- skills: 用户提到的技能列表
- project: 用户当前在做的项目
- preferences: 用户的偏好（如回复风格、详细程度等）
- has_new_info: 是否从对话中提取到了新信息

请以 JSON 格式输出，没有提到的字段保持为 null 或空。
只提取明确提到的信息，不要推测。""",
        ),
        ("human", "用户说: {message}"),
    ]
)

parser = JsonOutputParser(pydantic_object=ExtractedInfo)
extract_chain = extract_prompt | llm | parser


def extract_user_info(message: str) -> ExtractedInfo:
    result = extract_chain.invoke({"message": message})
    return ExtractedInfo(**result)


def update_profile_from_conversation(store, user_id: str, message: str):
    """从对话中抽取信息并更新 Redis 中的用户画像。"""
    extracted = extract_user_info(message)

    if not extracted.has_new_info:
        return store.get_or_create(user_id)

    profile = store.get_or_create(user_id)

    if extracted.name:
        profile.name = extracted.name
    if extracted.occupation:
        profile.occupation = extracted.occupation
    if extracted.skills:
        profile.domain_knowledge = list(set(profile.domain_knowledge + extracted.skills))
    if extracted.project:
        profile.current_project = extracted.project

    store.save(profile)
    return profile


if __name__ == "__main__":
    # store = RedisUserProfileStore()
    # for msg in [...]:  profile = update_profile_from_conversation(store, "user_001", msg)
    pass
