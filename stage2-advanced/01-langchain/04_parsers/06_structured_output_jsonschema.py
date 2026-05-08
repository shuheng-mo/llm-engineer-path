"""with_structured_output(json_schema) — 直接传 JSON Schema

对应课程章节：第五章 / 3.1 JSON Schema
"""
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"

json_schema = {
    "title": "Sentiment",
    "description": "情感分析结果",
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
            "description": "情感倾向，只能取值：positive/negative/neutral",
        },
        "confidence": {
            "type": "number", "minimum": 0, "maximum": 1,
            "description": "置信度，0到1之间的浮点数",
        },
        "keywords": {
            "type": "array", "items": {"type": "string"},
            "description": "关键情感词，数组元素为字符串",
        },
    },
    "required": ["sentiment", "confidence"],
}

model = ChatOpenAI(
    model="qwen-plus",
    api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL,
    temperature=0,
)

structured_model = model.with_structured_output(
    schema=json_schema,
    method="json_mode",
    include_raw=False,
)

input_text = """
请严格按照指定的 JSON Schema 输出情感分析结果：
1. 字段名必须为英文：sentiment/confidence/keywords；
2. sentiment 只能取值：positive/negative/neutral；
3. confidence 是 0-1 之间的浮点数；
4. 只输出 JSON，不要其他内容。

待分析文本：这个产品真的太棒了，我非常满意！
"""

try:
    result = structured_model.invoke(input_text)
    print("=== 情感分析结果 ===")
    print(result)
except Exception as e:
    print(f"调用失败：{e}")
