"""句子窗口检索（Sentence Window Retrieval）— 三步演示版

对应课程章节：二 / 1.4 步骤一~三
"""
import os
import re
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

load_dotenv()


def split_sentences(text: str) -> list:
    """中文分句：按句号、问号、感叹号切分。"""
    pattern = r"([。！？!?])"
    parts = re.split(pattern, text)
    sentences = []
    for i in range(0, len(parts) - 1, 2):
        sent = parts[i] + parts[i + 1]
        if sent.strip():
            sentences.append(sent.strip())
    return sentences


# 第一步：分句
text = "LangChain很强大。它支持RAG。RAG是检索增强生成。"
sentences = split_sentences(text)
print(sentences)

# 第二步：每句建立向量索引
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)
sentence_docs = [
    Document(page_content=sent, metadata={"sentence_idx": idx})
    for idx, sent in enumerate(sentences)
]
vectorstore = Chroma.from_documents(sentence_docs, embedding=embeddings)


# 第三步：检索时扩展窗口
def retrieve_with_window(query, sentences, vectorstore, window_size=1, k=3):
    results = vectorstore.similarity_search(query, k=k)
    expanded_results = []
    for doc in results:
        idx = doc.metadata["sentence_idx"]
        start = max(0, idx - window_size)
        end = min(len(sentences), idx + window_size + 1)
        expanded_results.append("".join(sentences[start:end]))
    return expanded_results


print(retrieve_with_window("什么是RAG？", sentences, vectorstore, window_size=1))
