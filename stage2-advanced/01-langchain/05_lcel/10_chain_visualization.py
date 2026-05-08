"""链的可视化与调试 — input/output schema、verbose、LangSmith

对应课程章节：第六章 / 5.3
"""
import os

# === 方法 1：打印链结构 ===
# chain = prompt | model | parser    # noqa: F821
# print("输入 Schema:", chain.input_schema.schema())
# print("输出 Schema:", chain.output_schema.schema())
# print("链的步骤:", chain.steps)


# === 方法 2：verbose 模式 ===
# from langchain.globals import set_verbose
# set_verbose(True)


# === 方法 3：LangSmith（生产环境推荐） ===
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# result = chain.invoke({"topic": "AI"})    # noqa: F821
