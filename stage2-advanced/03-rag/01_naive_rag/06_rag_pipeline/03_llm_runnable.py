"""RAG Pipeline 第三步：LLM Runnable（DashScope 兼容 OpenAI 协议）

对应课程章节：一 / 7.2.3
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# RAG 场景建议低温度，让回答更稳定
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)
