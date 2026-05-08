"""加载注意事项 — 编码处理 + lazy_load 流式处理大文件

对应课程章节：一 / 2.3
"""

from langchain_community.document_loaders import TextLoader



from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def process_document(doc):
    print(doc.page_content)


# 处理编码问题
loader = TextLoader(
    str(DATA_DIR.parent / "README.md"),
    encoding="utf-8",  # 显式指定编码
    autodetect_encoding=True,  # 或自动检测
)

# 大文件使用 lazy_load 逐个返回，减少内存占用
for doc in loader.lazy_load():
    process_document(doc)
