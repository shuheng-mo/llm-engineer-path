"""加载并校验 DASHSCOPE_API_KEY 环境变量

对应课程章节：第二章 / 5.4
"""

import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

print("API Key 加载成功！")
print(f"API Key 前缀：{api_key[:10]}...")
