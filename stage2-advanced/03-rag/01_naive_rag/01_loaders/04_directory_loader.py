"""DirectoryLoader — 批量目录加载

对应课程章节：一 / 2.2.4
"""
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# 加载目录下所有 .txt 文件
loader = DirectoryLoader(
    path="./documents/",
    glob="**/*.txt",            # 匹配模式
    loader_cls=TextLoader,      # 使用的加载器类
    show_progress=True,         # 显示进度条
)
documents = loader.load()
print(f"共加载 {len(documents)} 个文档")
