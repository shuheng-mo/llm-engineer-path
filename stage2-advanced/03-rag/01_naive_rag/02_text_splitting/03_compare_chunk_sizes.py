"""对比不同 chunk_size 的分割效果

对应课程章节：一 / 3 代码示例
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

loader = TextLoader(str(DATA_DIR.parent / "README.md"), encoding="utf-8")
pages = loader.load()

text = ""
for page in pages:
    text += page.page_content

# 对比不同 chunk_size 的效果
for size in [200, 500, 1000]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=int(size * 0.1),
    )
    chunks = splitter.split_text(text)
    print(f"chunk_size={size}: 生成 {len(chunks)} 个 chunks")
