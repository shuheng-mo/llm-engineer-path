"""PDF 阅读助手 — 多文件 + 来源追踪 + CLI 交互（带对话历史）

对应课程章节：一 / 8.5
"""

import os
import logging
from typing import List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.ERROR)


DATA_DIR = Path(__file__).resolve().parents[2] / "data"

load_dotenv()


class PDFReadingAssistant:
    """PDF 阅读助手类。"""

    def __init__(self, pdf_path: str = None, pdf_directory: str = None):
        self.llm = ChatOpenAI(
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            temperature=0.3,
        )

        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        )

        self.documents = self._load_documents(pdf_path, pdf_directory)
        self.chunks = self._split_documents(self.documents)

        self.vectorstore = self._create_vectorstore(self.chunks)
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 10},
        )

        self.rag_chain = self._create_rag_chain()
        self.chat_history: List = []

    def _load_documents(self, pdf_path: str, pdf_directory: str) -> List[Document]:
        documents = []
        if pdf_path:
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            print(f"✅ 已加载文件: {pdf_path}")

        if pdf_directory:
            loader = DirectoryLoader(
                pdf_directory,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True,
            )
            documents.extend(loader.load())
            print(f"✅ 已加载目录: {pdf_directory}")

        print(f"📄 共加载 {len(documents)} 个文档页面")
        return documents

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
        )
        chunks = splitter.split_documents(documents)
        print(f"📝 文档已分割为 {len(chunks)} 个片段")
        return chunks

    def _create_vectorstore(self, chunks: List[Document]) -> Chroma:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(DATA_DIR / "pdf_assistant_db"),
        )
        print("💾 向量数据库创建完成")
        return vectorstore

    def _format_docs_with_source(self, docs: List[Document]) -> str:
        formatted = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "未知来源")
            page = doc.metadata.get("page", "?")
            page_str = page + 1 if isinstance(page, int) else page
            formatted.append(
                f"[片段 {i + 1} | 来源: {os.path.basename(source)} | 第 {page_str} 页]\n"
                f"{doc.page_content}"
            )
        return "\n\n---\n\n".join(formatted)

    def _create_rag_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一个专业的 PDF 文档阅读助手。你的任务是根据提供的文档内容回答用户问题。

规则：
1. 只使用提供的文档内容回答问题
2. 如果文档中没有相关信息，请诚实告知
3. 在回答时，请指出信息来源（如"根据第X页..."）
4. 回答要准确、简洁、有条理

参考文档：
{context}""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        return (
            {
                "context": self.retriever | self._format_docs_with_source,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: self.chat_history,
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        answer = self.rag_chain.invoke(question)

        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        return answer

    def ask_with_contexts(self, question: str) -> tuple[str, list[str]]:
        """像 ask() 一样回答，但同时返回检索到的上下文片段（专为 Ragas 评估准备）。

        Ragas 的 SingleTurnSample 需要：
          - response：LLM 生成的回答
          - retrieved_contexts：检索器返回的纯文本片段列表

        Returns:
            (answer, retrieved_contexts) 元组
        """
        # 用 retriever 拿到原始 Document 列表（和 rag_chain 内部用的是同一个 retriever，
        # 不会"作弊"——检索结果完全一致）
        retrieved_docs = self.retriever.invoke(question)
        retrieved_contexts = [doc.page_content for doc in retrieved_docs]

        # 复用 ask() 拿到回答（自动维护 chat_history，但评估时应在外部 clear_history）
        answer = self.ask(question)

        return answer, retrieved_contexts

    def clear_history(self):
        self.chat_history = []
        print("🔄 对话历史已清除")


def main():
    assistant = PDFReadingAssistant(pdf_directory=str(DATA_DIR))

    print("\n💡 提示：输入问题开始对话，输入 'quit' 退出，输入 'clear' 清除历史\n")

    while True:
        question = input("🙋 你的问题: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            print("👋 再见！")
            break
        if question.lower() == "clear":
            assistant.clear_history()
            continue

        try:
            answer = assistant.ask(question)
            print(f"\n🤖 回答:\n{answer}\n")
            print("-" * 60)
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
