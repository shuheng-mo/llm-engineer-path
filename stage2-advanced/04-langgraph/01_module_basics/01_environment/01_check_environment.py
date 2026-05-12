"""校验环境变量是否配齐

对应课程章节：模块一 / 3.3
"""

import os

from dotenv import load_dotenv

load_dotenv()


def check_environment():
    required_keys = ["DASHSCOPE_API_KEY", "LANGSMITH_API_KEY"]
    for key in required_keys:
        if not os.getenv(key):
            print(f"缺少环境变量: {key}")
        else:
            print(f"{key}: 已配置")


if __name__ == "__main__":
    check_environment()
