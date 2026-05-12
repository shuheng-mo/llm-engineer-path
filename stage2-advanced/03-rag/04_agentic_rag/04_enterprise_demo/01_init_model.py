"""初始化 Qwen 模型（ChatTongyi）

对应课程章节：四 / 第四章 2.3

依赖:
uv pip install langchain langchain-community langchain-core langgraph dashscope chromadb
"""

from langchain_community.chat_models import ChatTongyi

# 在环境变量里配置：DASHSCOPE_API_KEY
llm = ChatTongyi(model="qwen-max", temperature=0)
