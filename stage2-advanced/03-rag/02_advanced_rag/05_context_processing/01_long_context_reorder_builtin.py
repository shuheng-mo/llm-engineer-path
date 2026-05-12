"""Long Context Reorder（内置版） — 缓解 Lost in the Middle

对应课程章节：二 / 5.2 方式一
"""

from langchain_community.document_transformers import LongContextReorder
from langchain_core.documents import Document

# 假设这是按相关性排序后的检索结果
docs = [
    Document(page_content="最相关的文档内容..."),
    Document(page_content="第二相关的文档内容..."),
    Document(page_content="第三相关的文档内容..."),
    Document(page_content="第四相关的文档内容..."),
    Document(page_content="第五相关的文档内容..."),
]

reorder = LongContextReorder()
reordered_docs = reorder.transform_documents(docs)

for i, doc in enumerate(reordered_docs, 1):
    print(f"位置 {i}: {doc.page_content[:20]}...")
