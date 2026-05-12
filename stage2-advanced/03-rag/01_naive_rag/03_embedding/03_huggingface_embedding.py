"""HuggingFace 本地 Embedding — sentence-transformers 直接跑（无需联网调 API）

对应课程章节：一 / 4.3.3（扩展）

依赖:
    rag group 已经装了 sentence-transformers；
    本地模型由 sentence-transformers 自动从 HuggingFace Hub 下载到 ~/.cache/huggingface/

适用场景：
    - 离线/内网部署，不能调云端 API
    - 中文语料，bge-large-zh 比 OpenAI/通义的通用 embedding 在中文上表现更好
    - 想跑大批量数据，本地推理避免按 token 付费

模型推荐（参考 notes.md）：
    - BAAI/bge-large-zh-v1.5      — 中文优化，1024 维，~1.3GB（首次下载慢）
    - BAAI/bge-small-zh-v1.5      — 同源轻量版，512 维，~100MB（演示推荐）
    - BAAI/bge-m3                 — 多语言（中英日韩等），1024 维
    - sentence-transformers/all-MiniLM-L6-v2  — 英文小模型，384 维，~80MB

注意：
    - 首次跑会下载模型（按上面列出的大小预估）
    - Apple Silicon 自动用 MPS 加速；想强制 CPU 改 model_kwargs={"device": "cpu"}
"""

from langchain_community.embeddings import HuggingFaceEmbeddings

# ============================================================
# 1. 初始化 — bge-small-zh-v1.5（小模型，演示快）
# ============================================================
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "mps"},  # Apple Silicon；Linux+CUDA 改 "cuda"，纯 CPU 改 "cpu"
    encode_kwargs={"normalize_embeddings": True},  # 归一化后可直接用点积当余弦相似度
)


# ============================================================
# 2. 单条嵌入
# ============================================================
text = "LangChain 是一个强大的 LLM 应用开发框架"
vector = embeddings.embed_query(text)
print(f"向量维度: {len(vector)}")  # bge-small-zh-v1.5 是 512
print(f"向量前5维: {vector[:5]}")


# ============================================================
# 3. 批量嵌入
# ============================================================
texts = [
    "什么是机器学习？",
    "深度学习和机器学习的区别",
    "如何入门人工智能",
    "RAG 是什么？",
]
vectors = embeddings.embed_documents(texts)
print(f"\n生成了 {len(vectors)} 个向量")


# ============================================================
# 4. 验证语义相似 —— "机器学习" 和 "深度学习" 应该比 "RAG" 更近
# ============================================================
import numpy as np


def cosine(a, b):
    return float(np.dot(a, b))  # 已 normalize，点积 == 余弦相似度


q_vec = embeddings.embed_query("ML 和 DL 有什么区别")
print("\n=== 语义相似度排序（应当机器学习相关的排前面） ===")
for txt, vec in sorted(
    zip(texts, vectors),
    key=lambda pair: cosine(q_vec, pair[1]),
    reverse=True,
):
    score = cosine(q_vec, vec)
    print(f"  {score:.4f}  {txt}")
