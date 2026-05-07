"""RAG Pipeline 端到端完整示例（loader→splitter→vectorstore→mmr retriever→chain→CLI）

对应课程章节：一 / 7.4
"""
import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 1. 模型配置
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 2. 文档处理
loader = PyPDFLoader("docs/LangChain.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", " ", ""],
)
chunks = splitter.split_documents(documents)

# 3. 向量存储
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)

# 4. 检索器（MMR 增加多样性）
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 10},
)


# 5. 构建 RAG Chain
def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[文档片段 {i + 1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """你是一个专业的文档问答助手。

参考资料：
{context}

请根据上述参考资料回答问题。如果资料中没有相关信息，请说明。""",
    ),
    ("human", "{question}"),
])

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)


# 6. 运行问答
if __name__ == "__main__":
    while True:
        question = input("\n请输入问题（输入 'quit' 退出）：")
        if question.lower() == "quit":
            break
        answer = rag_chain.invoke(question)
        print(f"\n回答：{answer}")
