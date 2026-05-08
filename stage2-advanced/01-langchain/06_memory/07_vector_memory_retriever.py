"""长期记忆通过 Retriever 注入 Prompt

对应课程章节：第七章 / 4.3
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 假设外部已经有 vectorstore / llm
# from .06_vector_memory_basic import vectorstore, llm


retriever = vectorstore.as_retriever(                                # noqa: F821
    search_kwargs={"k": 3, "filter": {"user_id": "user_001"}},
)


prompt_with_memory = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手。以下是关于用户的长期记忆：
{long_term_memory}

请根据这些信息为用户提供个性化的帮助。"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


def format_memories(docs: list) -> str:
    if not docs:
        return "暂无用户长期记忆"
    return "\n".join(f"- {doc.page_content}" for doc in docs)


chain = (
    {
        "long_term_memory": (lambda x: x["input"]) | retriever | format_memories,
        "history": lambda x: x.get("history", []),
        "input": lambda x: x["input"],
    }
    | prompt_with_memory
    | llm                                                            # noqa: F821
    | StrOutputParser()
)


result = chain.invoke({"input": "帮我写一段代码", "history": []})
print(result)
