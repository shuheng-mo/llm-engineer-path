"""把 Long Context Reorder 集成进 RAG 流程

对应课程章节：二 / 5.2 集成版
"""
from langchain_community.document_transformers import LongContextReorder


def rag_with_reorder(query: str, retriever, llm) -> str:
    docs = retriever.invoke(query)
    print(f"检索到 {len(docs)} 个文档")

    reorder = LongContextReorder()
    reordered_docs = reorder.transform_documents(docs)

    context = "\n\n".join(doc.page_content for doc in reordered_docs)
    prompt = f"""根据以下参考文档回答问题。

参考文档：
{context}

问题：{query}

答案："""
    return llm.invoke(prompt).content
