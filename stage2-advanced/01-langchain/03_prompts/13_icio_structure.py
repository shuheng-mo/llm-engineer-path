"""ICIO 框架 — Instruction / Context / Input / Output Format

对应课程章节：第四章 / 4.1
"""
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system",
     """
# Instruction（指令）
你是一位专业的技术文档撰写专家。

# Context（上下文）
你正在为一家科技公司撰写产品文档，目标读者是技术开发者。

# Output Format（输出格式）
请按以下格式输出：
1. 概述（1-2句话）
2. 核心功能（3-5个要点）
3. 使用示例
4. 注意事项
    """),
    ("human", "请为以下产品撰写文档：{product_description}"),
])
