"""Few-shot Prompt — 手动构造 + FewShotChatMessagePromptTemplate

对应课程章节：第四章 / 3.2
"""
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

# === 方式 1：手动构造 ===
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个情感分析专家。请分析文本的情感倾向，输出：正面、负面 或 中性。"),
    ("human", "这个产品太棒了，我非常满意！"),
    ("ai", "正面"),
    ("human", "服务态度很差，再也不来了。"),
    ("ai", "负面"),
    ("human", "产品一般，没什么特别的。"),
    ("ai", "中性"),
    ("human", "{text}"),
])

messages = template.format_messages(text="物流很快，包装也很好，好评！")


# === 方式 2：FewShotChatMessagePromptTemplate ===
examples = [
    {"input": "2+2等于多少？", "output": "2+2等于4"},
    {"input": "3乘以4是多少？", "output": "3乘以4等于12"},
    {"input": "10除以2的结果？", "output": "10除以2等于5"},
]

example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个数学计算助手，请回答数学问题。"),
    few_shot_prompt,
    ("human", "{question}"),
])

messages = final_prompt.format_messages(question="5加3等于多少？")
for msg in messages:
    print(f"[{msg.type}] {msg.content}")
