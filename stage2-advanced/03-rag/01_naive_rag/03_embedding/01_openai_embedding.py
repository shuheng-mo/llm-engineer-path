"""OpenAI Embedding — text-embedding-3-small

对应课程章节：一 / 4.3.1
"""
from langchain_openai import OpenAIEmbeddings

# 初始化 Embedding 模型（api_key 从环境变量 OPENAI_API_KEY 自动读取）
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 单条文本嵌入
text = "LangChain 是一个强大的 LLM 应用开发框架"
vector = embeddings.embed_query(text)
print(f"向量维度: {len(vector)}")
print(f"向量前5维: {vector[:5]}")

# 批量文本嵌入
texts = [
    "什么是机器学习？",
    "深度学习和机器学习的区别",
    "如何入门人工智能",
]
vectors = embeddings.embed_documents(texts)
print(f"生成了 {len(vectors)} 个向量")
