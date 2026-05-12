"""结构化用户画像 — Pydantic 模型 + JSON 序列化

对应课程章节：第七章 / 5.1
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    response_length: str = Field(default="medium", description="回复长度: short/medium/long")
    code_style: str = Field(default="clean", description="代码风格偏好")
    explanation_level: str = Field(default="intermediate", description="解释详细程度")
    language: str = Field(default="zh-CN", description="偏好语言")


class UserProfile(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")
    name: Optional[str] = Field(default=None, description="用户名称")
    occupation: Optional[str] = Field(default=None, description="职业")
    domain_knowledge: list[str] = Field(default_factory=list, description="领域知识")
    current_project: Optional[str] = Field(default=None, description="当前项目")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


if __name__ == "__main__":
    profile = UserProfile(
        user_id="user_001",
        name="小明",
        occupation="Python后端开发工程师",
        domain_knowledge=["Python", "FastAPI", "PostgreSQL", "Redis"],
        current_project="电商推荐系统",
        preferences=UserPreferences(
            response_length="short",
            code_style="clean",
            explanation_level="advanced",
            language="zh-CN",
        ),
    )
    print(profile.model_dump_json(indent=2))
