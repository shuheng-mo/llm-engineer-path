"""RunnableSequence — 顺序链（| 操作符等价于 RunnableSequence）

对应课程章节：第六章 / 3.2
"""

from langchain_core.runnables import RunnableSequence

# 假设已经有 prompt / model / parser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser

# 方式 1：使用 | 操作符（语法糖）
chain = prompt | model | parser  # noqa: F821

# 方式 2：显式使用 RunnableSequence
chain = RunnableSequence(first=prompt, middle=[model], last=parser)  # noqa: F821

# 两种方式完全等价
