"""对比 BM25 / 向量 / 混合三种检索效果

对应课程章节：二 / 3.4 第三步
"""
# 这是一个对比脚本，依赖 03_ensemble_hybrid.py 中已构建好的三个 retriever。
# 在实际使用时，把那三个 retriever 直接 import 过来或 inline 在这里。

query = "RecursiveCharacterTextSplitter 怎么用？"

print("=" * 60)
print(f" 查询: {query}")
print("=" * 60)

# BM25
print("\nBM25 检索结果（关键词匹配）:")
bm25_results = bm25_retriever.invoke(query)              # noqa: F821
for i, doc in enumerate(bm25_results[:3]):
    has = "RecursiveCharacterTextSplitter" in doc.page_content
    print(f"   {i + 1}. {'YES' if has else 'NO'} {doc.page_content[:60]}...")

# 向量
print("\n向量检索结果（语义相似）:")
vector_results = vector_retriever.invoke(query)          # noqa: F821
for i, doc in enumerate(vector_results[:3]):
    has = "RecursiveCharacterTextSplitter" in doc.page_content
    print(f"   {i + 1}. {'YES' if has else 'NO'} {doc.page_content[:60]}...")

# 混合
print("\n混合检索结果（综合）:")
hybrid_results = ensemble_retriever.invoke(query)        # noqa: F821
for i, doc in enumerate(hybrid_results[:3]):
    has = "RecursiveCharacterTextSplitter" in doc.page_content
    print(f"   {i + 1}. {'YES' if has else 'NO'} {doc.page_content[:60]}...")
