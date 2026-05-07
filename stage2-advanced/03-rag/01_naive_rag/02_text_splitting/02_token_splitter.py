"""TokenTextSplitter — Token 感知分割（适合精确控制 LLM 上下文长度）

对应课程章节：一 / 3.2.2
"""
from langchain_text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=200,                # Token 数量
    chunk_overlap=20,
    encoding_name="cl100k_base",   # GPT-4 使用的编码
)

text = "你的长文本..."
chunks = splitter.split_text(text)
print(f"共分成 {len(chunks)} 个 Token chunks")
