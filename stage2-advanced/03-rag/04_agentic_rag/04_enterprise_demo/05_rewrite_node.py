"""节点 3：查询重写（rewrite）

对应课程章节：四 / 第四章 4.4
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

system_rewrite = """你是一个查询重写专家。
看这输入的问题，它的检索结果质量很差。
请根据问题的本意，重新构思一个更好的搜索查询语句。
只输出新的查询语句，不要解释。"""

rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_rewrite),
        ("human", "原始问题: {question}"),
    ]
)

question_rewriter = rewrite_prompt | llm | StrOutputParser()  # noqa: F821


def rewrite(state):
    print("---NODE: 重写查询---")
    question = state["question"]
    better_question = question_rewriter.invoke({"question": question})
    print(f"---重写后的问题: {better_question}---")
    return {"question": better_question}
