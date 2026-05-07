"""句子窗口检索 — 封装为可复用的 SentenceWindowRetriever 类

对应课程章节：二 / 1.4 完整封装版本
"""
import os
import re
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

load_dotenv()


class SentenceWindowRetriever:
    def __init__(self, documents: list, window_size: int = 1):
        self.window_size = window_size
        self.sentences = []

        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        )

        for doc in documents:
            self.sentences.extend(self._split_sentences(doc.page_content))

        sentence_docs = [
            Document(page_content=sent, metadata={"idx": i})
            for i, sent in enumerate(self.sentences)
        ]
        self.vectorstore = Chroma.from_documents(sentence_docs, self.embeddings)
        print(f"✅ 索引完成：{len(self.sentences)} 个句子")

    def _split_sentences(self, text: str) -> list:
        parts = re.split(r"([。！？!?])", text)
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sent = (parts[i] + parts[i + 1]).strip()
            if sent:
                sentences.append(sent)
        return sentences

    def retrieve(self, query: str, k: int = 3) -> list:
        results = self.vectorstore.similarity_search(query, k=k)
        windows = []
        for doc in results:
            idx = doc.metadata["idx"]
            start = max(0, idx - self.window_size)
            end = min(len(self.sentences), idx + self.window_size + 1)
            windows.append({
                "matched": self.sentences[idx],
                "window": "".join(self.sentences[start:end]),
            })
        return windows


if __name__ == "__main__":
    docs = [Document(page_content="LangChain是框架。它很强大。可以做RAG。RAG是检索增强生成。它很有用。")]
    retriever = SentenceWindowRetriever(docs, window_size=1)
    for r in retriever.retrieve("什么是RAG？"):
        print(f"匹配: {r['matched']}")
        print(f"窗口: {r['window']}\n")
