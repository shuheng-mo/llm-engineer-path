"""RunnableBranch — 条件分支

对应课程章节：第六章 / 3.4
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch


def classify_question(input_dict):
    question = input_dict["question"].lower()
    if "代码" in question or "编程" in question:
        return "code"
    if "数学" in question or "计算" in question:
        return "math"
    return "general"


code_chain = ChatPromptTemplate.from_template("你是编程专家。请回答：{question}") | model  # noqa: F821
math_chain = ChatPromptTemplate.from_template("你是数学家。请回答：{question}") | model  # noqa: F821
general_chain = ChatPromptTemplate.from_template("请回答：{question}") | model  # noqa: F821

branch = RunnableBranch(
    (lambda x: classify_question(x) == "code", code_chain),
    (lambda x: classify_question(x) == "math", math_chain),
    general_chain,  # 默认分支
)


result1 = branch.invoke({"question": "如何用 Python 写冒泡排序？"})
result2 = branch.invoke({"question": "1+1等于多少？"})
result3 = branch.invoke({"question": "今天天气怎么样？"})
