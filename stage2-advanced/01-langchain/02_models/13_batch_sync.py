"""同步批量调用 model.batch() + 控制并发

对应课程章节：第三章 / 5.2
"""

import os
import time

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

model = init_chat_model(
    "qwen-max",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
    temperature=0.7,
)


# === 基础用法 ===
inputs = [
    [HumanMessage(content="Python 是什么？")],
    [HumanMessage(content="Java 是什么？")],
    [HumanMessage(content="Go 是什么？")],
]
responses = model.batch(inputs)
for i, response in enumerate(responses):
    print(f"问题 {i + 1}: {response.content[:50]}...")


# === 控制并发数 ===
def call_model(x):
    start = time.time()
    print(f"开始：{x} 时间：{start:.2f}")
    result = model.invoke(x)
    end = time.time()
    print(f"结束：{x} 时间：{end:.2f} 耗时：{end - start:.2f}s")
    return result


runnable = RunnableLambda(call_model)
inputs = [f"请用一句话介绍 {lang}" for lang in ["Python", "Java", "Go", "C", "C#", "Rust"]]

start_total = time.time()
responses = runnable.batch(inputs, config=RunnableConfig(max_concurrency=3))
print("总耗时：", time.time() - start_total)
print(responses)
