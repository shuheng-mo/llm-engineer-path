"""复杂参数校验 — Literal / field_validator / Optional

对应课程章节：第八章 / 2.2.3
"""

from typing import Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator


class TranslationInput(BaseModel):
    """翻译工具的输入参数"""

    text: str = Field(description="要翻译的文本内容", min_length=1, max_length=5000)
    source_lang: str = Field(default="auto", description="源语言代码")
    target_lang: str = Field(description="目标语言代码")

    @field_validator("target_lang")
    @classmethod
    def validate_target_lang(cls, v):
        supported = ["zh", "en", "ja", "ko", "fr", "de"]
        if v not in supported:
            raise ValueError(f"不支持的目标语言: {v}，支持: {supported}")
        return v


class EmailInput(BaseModel):
    """发送邮件工具的输入参数"""

    to: str = Field(description="收件人邮箱地址")
    subject: str = Field(description="邮件主题", max_length=200)
    body: str = Field(description="邮件正文内容")
    priority: Literal["low", "normal", "high"] = Field(default="normal")
    cc: Optional[str] = Field(default=None, description="抄送人邮箱地址（可选）")


@tool(args_schema=TranslationInput)
def translate(text: str, source_lang: str, target_lang: str) -> str:
    """将文本从源语言翻译为目标语言。"""
    return f"[模拟翻译] {text} ({source_lang} -> {target_lang})"


@tool(args_schema=EmailInput)
def send_email(to: str, subject: str, body: str, priority: str = "normal", cc: str = None) -> str:
    """发送电子邮件。"""
    cc_info = f"，抄送: {cc}" if cc else ""
    return f"邮件已发送至 {to}{cc_info}，主题: {subject}，优先级: {priority}"
