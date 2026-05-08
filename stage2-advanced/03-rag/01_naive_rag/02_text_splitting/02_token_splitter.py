"""TokenTextSplitter — Token 感知分割（适合精确控制 LLM 上下文长度）

对应课程章节：一 / 3.2.2
"""

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import TokenTextSplitter


from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

loader = PyMuPDFLoader(str(DATA_DIR / "文档1.pdf"))
pages = loader.load()

text = ""

for page in pages:
    text += page.page_content

splitter = TokenTextSplitter(
    chunk_size=200,  # Token 数量
    chunk_overlap=20,
    encoding_name="cl100k_base",  # GPT-4 使用的编码
)


chunks = splitter.split_text(text)
print(f"共分成 {len(chunks)} 个 Token chunks")
