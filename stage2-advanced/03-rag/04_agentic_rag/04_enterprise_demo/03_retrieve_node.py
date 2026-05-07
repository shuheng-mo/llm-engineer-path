"""节点 1：检索（retrieve）

对应课程章节：四 / 第四章 4.2
"""
def retrieve(state):
    print("---NODE: 检索中---")
    question = state["question"]
    documents = retriever.invoke(question)  # noqa: F821 — retriever 由外部注入
    return {"documents": documents, "question": question}
