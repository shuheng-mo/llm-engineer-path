"""ChatPromptTemplate 基本用法 — from_messages + format_messages

对应课程章节：第四章 / 2.2
"""
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# === 方式 1：从消息列表创建 ===
template = ChatPromptTemplate.from_messages([
    ("system", "你是一位专业的{role}，请用{language}回答问题。"),
    ("human", "{question}"),
])

messages = template.format_messages(
    role="技术顾问",
    language="简体中文",
    question="什么是微服务架构？",
)
for msg in messages:
    print(f"{msg.type}: {msg.content}")


# === 方式 2：使用 Message 类 ===
system_template = SystemMessagePromptTemplate.from_template(
    "你是一位专业的{role}，名字叫{name}"
)
human_template = HumanMessagePromptTemplate.from_template("{user_input}")

template = ChatPromptTemplate.from_messages([system_template, human_template])

messages = template.format_messages(role="技术顾问", name="小智", user_input="什么是大模型？")
for msg in messages:
    print(f"{msg.type}: {msg.content}")
