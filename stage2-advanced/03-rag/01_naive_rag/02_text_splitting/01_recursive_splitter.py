"""RecursiveCharacterTextSplitter — 推荐的字符级递归分割器

对应课程章节：一 / 3.2.1
"""

from langchain_community.document_loaders import (
    PyPDFLoader,
    PyMuPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

import logging

logging.getLogger("pypdf").setLevel(logging.ERROR)

# loader = PyPDFLoader("../../data/aie-market-analysis.pdf")
loader = PyMuPDFLoader("../../data/文档1.pdf")  # 中文效果比pypdf更加鲁棒
pages = loader.load()

text = ""
for page in pages:
    text += page.page_content

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 每个 chunk 的最大字符数
    chunk_overlap=50,  # chunk 之间的重叠字符数
    length_function=len,
    separators=[  # 分隔符优先级（从高到低）
        "\n\n",  # 段落
        "\n",  # 换行
        "。",  # 中文句号
        ".",  # 英文句号
        " ",  # 空格
        "",  # 字符级别
    ],
)

chunks = splitter.split_text(text)

# 测试loader和splitter是否生效
# print(f"页数: {len(pages)}")
# print(f"第一页前 200 字: {pages[0].page_content[:200]!r}")
# print(f"text 总长度: {len(text)}")
# print(f"chunks 数量: {len(chunks)}")


for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}: {len(chunk)} 字符")
    print(chunk[:1000] + "...")
    print("-" * 40)
