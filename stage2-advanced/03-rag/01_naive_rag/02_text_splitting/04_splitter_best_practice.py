"""分割最佳实践 — split_documents 保留 metadata

对应课程章节：一 / 3.4
"""

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# 1. 加载文档
loader = PyMuPDFLoader(str(DATA_DIR / "文档1.pdf"))
documents = loader.load()

# 2. 创建分割器（推荐配置）
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
)

# 3. 分割文档（保留元数据）
chunks = splitter.split_documents(documents)

# 4. 验证分割结果
print(f"原始文档数: {len(documents)}")
print(f"分割后 chunks 数: {len(chunks)}")
print(f"平均 chunk 长度: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f}")
