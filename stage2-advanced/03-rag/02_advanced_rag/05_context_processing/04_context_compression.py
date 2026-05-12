"""上下文压缩（自定义版本） — 用 LLM 把每个文档抽取出与问题相关的句子

对应课程章节：二 / 5.3 方式二
"""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

compress_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """从给定文档中提取与问题相关的内容。

要求：
1. 只保留与问题直接相关的句子
2. 保持原文表述，不要改写
3. 如果没有相关内容，返回"无相关内容"
4. 不要添加任何解释

文档内容：
{document}""",
        ),
        ("human", "问题：{question}\n\n相关内容："),
    ]
)


def compress_document(doc_content: str, question: str, llm) -> str:
    response = (compress_prompt | llm).invoke({"document": doc_content, "question": question})
    return response.content


def compress_all_documents(docs: list, question: str, llm) -> list:
    compressed = []
    for doc in docs:
        compressed_content = compress_document(doc.page_content, question, llm)
        if compressed_content != "无相关内容":
            compressed.append(Document(page_content=compressed_content, metadata=doc.metadata))
    return compressed


if __name__ == "__main__":
    # 把 base_retriever / llm 传进来跑就行
    pass
