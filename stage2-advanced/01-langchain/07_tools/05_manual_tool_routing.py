"""手动工具路由（不依赖 Agent）— LLM 输出 JSON 决策 → 执行 → 整合

对应课程章节：第八章 / 3.1.1
"""

import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)


@tool
def calculator(expression: str) -> str:
    """计算数学表达式。"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气。"""
    weather_db = {"北京": "晴天 25°C", "上海": "多云 28°C", "深圳": "小雨 30°C"}
    return weather_db.get(city, f"未找到 {city} 的天气")


tools = {"calculator": calculator, "get_weather": get_weather}


def create_tool_prompt():
    descriptions = []
    for name, t in tools.items():
        descriptions.append(f"""
工具名称: {name}
功能描述: {t.description}
参数格式: {json.dumps(t.args_schema.model_json_schema(), ensure_ascii=False, indent=2)}
""")
    return f"""你是一个智能助手，可以使用以下工具来帮助用户：

{"".join(descriptions)}

当用户的问题需要使用工具时，请按以下 JSON 格式输出：
{{
    "need_tool": true,
    "tool_name": "工具名称",
    "tool_args": {{"参数名": "参数值"}}
}}

当不需要工具时，请按以下格式输出：
{{
    "need_tool": false,
    "answer": "你的回答"
}}

请只输出 JSON，不要有其他内容。
"""


def process_query(query: str) -> str:
    system_prompt = create_tool_prompt()
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]

    response = llm.invoke(messages)
    response_text = response.content

    try:
        clean_text = response_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1]
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
        decision = json.loads(clean_text.strip())
    except json.JSONDecodeError:
        return f"解析错误，原始响应: {response_text}"

    if not decision.get("need_tool", False):
        return decision.get("answer", "无法回答")

    tool_name = decision.get("tool_name")
    tool_args = decision.get("tool_args", {})
    if tool_name not in tools:
        return f"未知工具: {tool_name}"

    tool_result = tools[tool_name].invoke(tool_args)
    print(f"[调试] 工具 {tool_name} 执行结果: {tool_result}")

    final_messages = [
        SystemMessage(content="请根据工具执行结果，用自然语言回答用户的问题。"),
        HumanMessage(
            content=f"""
用户问题: {query}
工具执行结果: {tool_result}

请给出友好的回答：
"""
        ),
    ]
    return llm.invoke(final_messages).content


if __name__ == "__main__":
    print("=" * 50)
    print("测试 1: 数学计算")
    print(process_query("请帮我计算 (15 + 27) * 3 等于多少"))

    print("\n" + "=" * 50)
    print("测试 2: 天气查询")
    print(process_query("北京今天天气怎么样？"))

    print("\n" + "=" * 50)
    print("测试 3: 普通问题")
    print(process_query("Python 是什么？"))
