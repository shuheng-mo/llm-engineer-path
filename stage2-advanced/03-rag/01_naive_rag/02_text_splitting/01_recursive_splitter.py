"""RecursiveCharacterTextSplitter — 推荐的字符级递归分割器

对应课程章节：一 / 3.2.1
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("docs/LangChain.pdf")
pages = loader.load()

text = ""
for page in pages:
    text += page.page_content

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,            # 每个 chunk 的最大字符数
    chunk_overlap=50,          # chunk 之间的重叠字符数
    length_function=len,
    separators=[               # 分隔符优先级（从高到低）
        "\n\n",   # 段落
        "\n",      # 换行
        "。",       # 中文句号
        ".",        # 英文句号
        " ",        # 空格
        "",         # 字符级别
    ],
)

chunks = splitter.split_text(text)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}: {len(chunk)} 字符")
    print(chunk[:1000] + "...")
    print("-" * 40)
