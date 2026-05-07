"""组装 RAG Chain — RunnableParallel 与字典两种写法

对应课程章节：一 / 7.3
"""
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# 假设外部已准备好 retriever、format_docs、RAG_PROMPT、llm、output_parser
# from .01_context_runnable import format_docs ...

# 方式 1：RunnableParallel
rag_chain = (
    RunnableParallel(
        context=retriever | format_docs,    # noqa: F821
        question=RunnablePassthrough(),
    )
    | RAG_PROMPT                            # noqa: F821
    | llm                                   # noqa: F821
    | output_parser                         # noqa: F821
)

# 方式 2：字典写法（更简洁，等价）
rag_chain = (
    {
        "context": retriever | format_docs, # noqa: F821
        "question": RunnablePassthrough(),
    }
    | RAG_PROMPT                            # noqa: F821
    | llm                                   # noqa: F821
    | output_parser                         # noqa: F821
)

if __name__ == "__main__":
    answer = rag_chain.invoke("什么是 LangChain？")
    print(answer)
