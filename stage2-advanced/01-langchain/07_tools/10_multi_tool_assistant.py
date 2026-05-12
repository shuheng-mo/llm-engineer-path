"""实战：多工具助手 — 计算器 / 天气 / 翻译 / 情感分析

对应课程章节：第八章 / 5.3
"""

"""多功能助手 - 完整实现：计算器、天气查询、翻译、文本分析"""
import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)


# === 工具 1：计算器 ===
class CalculatorInput(BaseModel):
    expression: str = Field(description="数学表达式，如 '2 + 3 * 4'")


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """执行数学计算。支持加减乘除和括号运算。"""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误：包含不允许的字符"
        return f"{expression} = {eval(expression)}"
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except Exception as e:
        return f"计算错误：{str(e)}"


# === 工具 2：天气查询 ===
class WeatherInput(BaseModel):
    city: str = Field(description="要查询天气的城市名称")


@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """查询指定城市的当前天气状况。"""
    weather_db = {
        "北京": {"condition": "晴天", "temp": 25, "humidity": 40},
        "上海": {"condition": "多云", "temp": 28, "humidity": 65},
        "广州": {"condition": "小雨", "temp": 30, "humidity": 80},
        "深圳": {"condition": "阴天", "temp": 29, "humidity": 70},
        "杭州": {"condition": "晴天", "temp": 27, "humidity": 55},
    }
    if city in weather_db:
        w = weather_db[city]
        return f"{city}天气：{w['condition']}，温度 {w['temp']}°C，湿度 {w['humidity']}%"
    return f"抱歉，暂无 {city} 的天气数据"


# === 工具 3：翻译 ===
class TranslateInput(BaseModel):
    text: str = Field(description="要翻译的文本内容")
    target_lang: Literal["中文", "英文", "日文"] = Field(description="目标语言")


@tool(args_schema=TranslateInput)
def translate(text: str, target_lang: str) -> str:
    """将文本翻译成目标语言。"""
    translations = {
        "你好": {"英文": "Hello", "日文": "こんにちは"},
        "Hello": {"中文": "你好", "日文": "こんにちは"},
        "谢谢": {"英文": "Thank you", "日文": "ありがとう"},
    }
    if text in translations and target_lang in translations[text]:
        return f"翻译结果：{translations[text][target_lang]}"
    return f"[模拟翻译] 将 '{text}' 翻译为{target_lang}的结果"


# === 工具 4：情感分析 ===
class SentimentInput(BaseModel):
    text: str = Field(description="要分析情感的文本内容")


@tool(args_schema=SentimentInput)
def analyze_sentiment(text: str) -> str:
    """分析文本的情感倾向（积极、消极或中性）。"""
    positive_words = ["好", "棒", "喜欢", "开心", "优秀", "满意", "感谢", "爱"]
    negative_words = ["差", "糟", "讨厌", "失望", "难过", "生气", "烦", "坏"]

    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)

    if pos_count > neg_count:
        sentiment = "积极"
        confidence = min(0.9, 0.5 + pos_count * 0.1)
    elif neg_count > pos_count:
        sentiment = "消极"
        confidence = min(0.9, 0.5 + neg_count * 0.1)
    else:
        sentiment = "中性"
        confidence = 0.5

    return f"情感分析结果：{sentiment}（置信度：{confidence:.0%}）"


class MultiToolAssistant:
    def __init__(self):
        self.tools = [calculator, get_weather, translate, analyze_sentiment]
        self.tool_map = {t.name: t for t in self.tools}
        self.llm_with_tools = llm.bind_tools(self.tools)

        self.system_prompt = """你是一个智能助手，可以使用多种工具来帮助用户：

1. calculator - 数学计算
2. get_weather - 天气查询
3. translate - 文本翻译
4. analyze_sentiment - 情感分析

请根据用户的问题，选择合适的工具来回答。如果问题不需要使用工具，直接回答即可。
回答时请使用友好、自然的语言。"""

    def chat(self, query: str, verbose: bool = True) -> str:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=query),
        ]

        response = self.llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        if verbose:
            print(f"\n{'=' * 40}")
            print(f"[检测到 {len(response.tool_calls)} 个工具调用]")

        for tc in response.tool_calls:
            name, args, tid = tc["name"], tc["args"], tc["id"]
            if verbose:
                print(f"  📌 调用: {name}")
                print(f"     参数: {args}")
            result = (
                self.tool_map[name].invoke(args) if name in self.tool_map else f"未知工具: {name}"
            )
            if verbose:
                print(f"     结果: {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=tid))

        if verbose:
            print(f"{'=' * 40}\n")

        return self.llm_with_tools.invoke(messages).content


def main():
    assistant = MultiToolAssistant()

    print("=" * 60)
    print("欢迎使用多功能助手！")
    print("支持功能：数学计算、天气查询、翻译、情感分析")
    print("输入 'quit' 退出")
    print("=" * 60)

    test_queries = [
        "帮我计算一下 (100 + 50) * 2 - 30",
        "北京和上海的天气怎么样？",
        "把'你好'翻译成英文",
        "分析一下这句话的情感：今天真是太开心了，考试成绩非常满意！",
        "Python 是什么编程语言？",  # 不需要工具
    ]

    print("\n📝 运行预设测试用例:\n")
    for i, query in enumerate(test_queries, 1):
        print(f"\n【测试 {i}】用户: {query}")
        print("-" * 40)
        print(f"助手: {assistant.chat(query)}")
        print()

    print("\n" + "=" * 60)
    print("进入交互模式，请输入您的问题：\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == "quit":
                print("再见！")
                break
            if not user_input:
                continue
            print(f"Assistant: {assistant.chat(user_input)}\n")
        except KeyboardInterrupt:
            print("\n再见！")
            break


if __name__ == "__main__":
    main()
