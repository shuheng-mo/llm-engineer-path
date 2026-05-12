"""纠错 JSON 解析器 — 清理 markdown / 修复尾逗号 / LLM 兜底修复

对应课程章节：第五章 / 4.1
"""

import json
import os
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


class RobustJsonParser:
    """鲁棒的 JSON 解析器"""

    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or ChatOpenAI(
            model="qwen-max",
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            temperature=0,
        )

    def _clean_json_string(self, text: str) -> str:
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        json_match = re.search(r"[\{\[]", text)
        if json_match:
            text = text[json_match.start() :]
        for i in range(len(text) - 1, -1, -1):
            if text[i] in "}]":
                text = text[: i + 1]
                break
        return text.strip()

    def _fix_common_errors(self, text: str) -> str:
        text = text.replace("'", '"')
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)
        text = re.sub(r"(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', text)
        return text

    def parse(self, text: str) -> dict:
        # 1. 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 清理后解析
        cleaned = self._clean_json_string(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. 修复常见错误
        fixed = self._fix_common_errors(cleaned)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # 4. 最后兜底：让 LLM 修复
        fix_prompt = f"""以下文本应该是 JSON 格式，但有一些错误。请修复并只返回正确的 JSON：

{text}

只返回修复后的 JSON，不要其他内容。"""

        response = self.llm.invoke(fix_prompt)
        return json.loads(self._clean_json_string(response.content))


if __name__ == "__main__":
    parser = RobustJsonParser()

    test_cases = [
        '```json\n{"name": "test"}\n```',  # Markdown 包裹
        "{'name': 'test'}",  # 单引号
        '{"items": [1, 2, 3,]}',  # 尾部逗号
        'Here is the result: {"value": 42}',  # 前置文本
    ]
    for test in test_cases:
        result = parser.parse(test)
        print(f"输入: {test[:30]}... => 输出: {result}")
