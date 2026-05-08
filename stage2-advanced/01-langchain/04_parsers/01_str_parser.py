"""StrOutputParser — 字符串解析器 + 流式输出

对应课程章节：第五章 / 2.1
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

parser = StrOutputParser()
model = init_chat_model(
    model="qwen-max", model_provider="openai",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([("human", "用一句话介绍 {topic}")])
chain = prompt | model | parser

# 一次性
result = chain.invoke({"topic": "Python"})
print(type(result))
print(result)


# 流式
def stream_output(topic):
    print(f"正在生成关于 {topic} 的介绍，此模式为流式输出：\n")
    for chunk in chain.stream({"topic": topic}):
        print(chunk, end="", flush=True)
    print("\n\n--- 生成完毕 ---")


if __name__ == "__main__":
    stream_output("Python")
