"""RunnableLambda — 把普通函数包装成 Runnable

对应课程章节：第六章 / 3.6
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda


def format_input(text: str) -> dict:
    return {"topic": text.strip()}


def format_output(response) -> str:
    return f"【AI回答】\n{response.content}"


chain = (
    RunnableLambda(format_input)
    | ChatPromptTemplate.from_template("请简要介绍：{topic}")
    | model  # noqa: F821
    | RunnableLambda(format_output)
)

result = chain.invoke("  人工智能  ")
print(result)
