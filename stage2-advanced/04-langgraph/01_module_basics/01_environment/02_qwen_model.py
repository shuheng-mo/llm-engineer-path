"""千问模型基础调用（ChatTongyi）

对应课程章节：模块一 / 3.3
"""

import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

load_dotenv()

llm = ChatTongyi(
    model="qwen-max",  # 或 qwen-plus / qwen-max
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
    top_p=0.9,
)

if __name__ == "__main__":
    response = llm.invoke("你好，请介绍一下 LangGraph")
    print(response.content)
