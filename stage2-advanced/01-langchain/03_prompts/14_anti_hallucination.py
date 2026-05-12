"""防幻觉 Prompt 三档策略 — 明示不确定 / 引用要求 / 自我检查

对应课程章节：第四章 / 4.2
"""

from langchain_core.prompts import ChatPromptTemplate

# 策略 1：明确告知不确定时的行为
anti_hallucination_v1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个严谨的知识助手。

重要规则：
- 只回答你确定知道的信息
- 如果不确定，请明确说"我不确定"或"我没有这方面的信息"
- 不要编造或猜测事实
- 如果信息可能过时，请提醒用户核实""",
        ),
        ("human", "{question}"),
    ]
)


# 策略 2：要求引用来源
anti_hallucination_v2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个严谨的研究助手。

回答规则：
1. 只陈述有据可查的事实
2. 区分"事实"和"观点"
3. 对于统计数据，说明数据来源和时效性
4. 使用"据报道"、"研究表明"等表述，避免绝对化陈述""",
        ),
        ("human", "{question}"),
    ]
)


# 策略 3：自我检查步骤
anti_hallucination_v3 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个谨慎的 AI 助手。

回答步骤：
1. 先理解问题
2. 检索你知道的相关信息
3. 评估信息的可靠性（确定/可能/不确定）
4. 只输出"确定"和"可能"级别的信息
5. 对"可能"级别的信息加上提示语

如果整个问题都属于"不确定"级别，请诚实告知。""",
        ),
        ("human", "{question}"),
    ]
)
