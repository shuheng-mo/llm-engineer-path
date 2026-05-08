"""动态选择示例 — SemanticSimilarityExampleSelector（语义相似度）

对应课程章节：第四章 / 3.3
"""
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import OpenAIEmbeddings

examples = [
    {"input": "我今天很开心", "output": "正面"},
    {"input": "这个产品太棒了", "output": "正面"},
    {"input": "服务很差劲", "output": "负面"},
    {"input": "我很失望", "output": "负面"},
    {"input": "还行吧，一般般", "output": "中性"},
    {"input": "没什么特别的感觉", "output": "中性"},
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2,                              # 选择最相似的 2 个示例
)

example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
dynamic_few_shot = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=example_selector,
    input_variables=["input"],
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "分析文本情感，输出：正面、负面 或 中性"),
    dynamic_few_shot,
    ("human", "{input}"),
])

messages = final_prompt.format_messages(input="这个体验真的太糟糕了")
for msg in messages:
    print(f"[{msg.type}] {msg.content}")
