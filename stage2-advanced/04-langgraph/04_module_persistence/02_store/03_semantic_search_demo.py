"""Store 语义搜索 — 用自然语言查询记忆

对应课程章节：模块四 / 3.3.2
"""

import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langgraph.store.memory import InMemoryStore

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

store = InMemoryStore(index={"dims": 1536, "embed": embeddings})

memories = [
    "我喜欢吃意大利菜，尤其是披萨和意面",
    "我最近在学习 Python 和机器学习",
    "我养了一只叫 Luna 的猫",
    "我每周末都去健身房锻炼",
]

for i, memory in enumerate(memories):
    store.put(("user_memories", "user_123"), key=str(i), value={"text": memory})

print("问：用户的饮食习惯是什么？")
results = store.search(("user_memories", "user_123"), query="用户的饮食习惯是什么？", limit=2)
for item in results:
    print(item.value["text"])
