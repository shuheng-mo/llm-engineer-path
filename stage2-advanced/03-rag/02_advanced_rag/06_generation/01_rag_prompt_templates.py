"""RAG 专用 Prompt 三档模板：基础 / 带引用 / 严格防幻觉

对应课程章节：二 / 6.1
"""

from langchain_core.prompts import ChatPromptTemplate

# 基础版：最简 RAG Prompt
BASIC_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个问答助手。请根据以下参考文档回答问题。
如果文档中没有相关信息，请说"根据提供的资料无法回答这个问题"。

参考文档：
{context}""",
        ),
        ("human", "{question}"),
    ]
)


# 进阶版：带引用编号的 Prompt
CITATION_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个专业的文档问答助手。

【任务】根据参考文档回答用户问题

【规则】
1. 只使用参考文档中的信息，不要使用你自己的知识
2. 在回答中使用 [1]、[2] 等标注引用了哪个文档
3. 如果文档中没有答案，直接说"根据现有资料无法回答"
4. 回答要简洁、准确、有条理

【参考文档】
{context}""",
        ),
        ("human", "{question}"),
    ]
)


def format_docs_with_id(docs):
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        formatted.append(f"[文档{i}] 来源: {source}\n{doc.page_content}")
    return "\n\n".join(formatted)


# 严格版：防幻觉 Prompt
STRICT_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个严谨的问答助手。

【核心原则】宁可说"不知道"，也不要编造答案

【回答规则】
1. 必须基于参考文档回答，绝对不能使用文档之外的信息
2. 如果文档只能部分回答问题，说明哪部分能回答，哪部分不能
3. 对于事实性问题，必须在文档中找到明确依据才能回答
4. 回答时标注依据来自哪个文档

【参考文档】
{context}

【无法回答时的标准回复】
"根据提供的参考文档，无法找到关于[问题主题]的相关信息。建议您查阅其他资料或提供更多相关文档。"
""",
        ),
        ("human", "{question}"),
    ]
)
