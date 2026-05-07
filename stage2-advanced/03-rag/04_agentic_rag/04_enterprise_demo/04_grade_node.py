"""节点 2：文档相关性评分（grade_documents）

对应课程章节：四 / 第四章 4.3
"""
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    """对检索文档相关性的二元评分。"""

    binary_score: str = Field(description="文档是否与问题相关，'yes' 或 'no'")


structured_llm_grader = llm.with_structured_output(GradeDocuments)  # noqa: F821

system = """你是一名专业的文档评估员。
请评估检索到的文档是否与用户的问题相关。
如果文档包含关键词或语义相关的含义，请评为 'yes'，否则评为 'no'。"""

grade_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "检索文档: \n\n {document} \n\n 用户问题: {question}"),
])

retrieval_grader = grade_prompt | structured_llm_grader


def grade_documents(state):
    print("---NODE: 评估文档相关性---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs, relevant_flag = [], "no"
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        if score.binary_score == "yes":
            print("---文档相关---")
            filtered_docs.append(d)
            relevant_flag = "yes"
        else:
            print("---文档无关，忽略---")

    return {"documents": filtered_docs, "question": question, "relevance": relevant_flag}
