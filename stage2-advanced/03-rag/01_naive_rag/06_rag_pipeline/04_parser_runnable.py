"""RAG Pipeline 第四步：StrOutputParser 把 AIMessage 解成纯字符串

对应课程章节：一 / 7.2.4
"""
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()
