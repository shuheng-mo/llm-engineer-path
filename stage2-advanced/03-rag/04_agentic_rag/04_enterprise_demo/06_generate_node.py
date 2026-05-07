"""节点 4：最终答案生成（generate）

对应课程章节：四 / 第四章 4.5
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template(
    """基于以下上下文回答问题:
    {context}

    问题: {question}
    """
)

rag_chain = rag_prompt | llm | StrOutputParser()  # noqa: F821


def generate(state):
    print("---NODE: 生成最终答案---")
    question = state["question"]
    documents = state["documents"]
    return {"generation": rag_chain.invoke({"context": documents, "question": question})}
