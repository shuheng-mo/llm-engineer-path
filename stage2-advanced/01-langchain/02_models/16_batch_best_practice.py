"""批量调用最佳实践 — return_exceptions + tqdm 进度

对应课程章节：第三章 / 5.5

依赖:
uv pip install tqdm
"""

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from tqdm import tqdm

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

model = init_chat_model(
    "qwen-plus",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)


# === 1. 错误处理 — return_exceptions=True ===
inputs = ["问题1", "问题2", "问题3"]

responses = model.batch(
    inputs,
    config=RunnableConfig(max_concurrency=2),
    return_exceptions=True,
)
for i, response in enumerate(responses):
    if isinstance(response, Exception):
        print(f"问题 {i + 1} 失败: {response}")
    else:
        print(f"问题 {i + 1} 成功: {response.content[:50]}...")


# === 2. tqdm 进度条 ===
inputs = [f"介绍编程语言 {i}" for i in range(10)]
batch_size = 3
results = []
for i in tqdm(range(0, len(inputs), batch_size)):
    batch = inputs[i : i + batch_size]
    batch_results = model.batch(batch)
    results.extend(batch_results)
