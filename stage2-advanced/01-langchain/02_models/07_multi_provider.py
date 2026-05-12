"""多 Provider 切换 — 工厂函数统一接 OpenAI/Anthropic/Google/Deepseek/Qwen

对应课程章节：第三章 / 3.8

依赖:
uv pip install langchain-anthropic langchain-google-genai
"""

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")


def get_model(provider: str, **kwargs):
    models = {
        "openai": lambda: ChatOpenAI(
            model=kwargs.get("model", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        "anthropic": lambda: ChatAnthropic(
            model=kwargs.get("model", "claude-4.0"),
            api_key=os.getenv("ClAUDE_API_KEY"),
        ),
        "google": lambda: ChatGoogleGenerativeAI(
            model=kwargs.get("model", "gemini-2.0-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
        ),
        "deepseek": lambda: ChatOpenAI(
            model=kwargs.get("model", "deepseek-chat"),
            base_url=os.getenv("DeepseekAPI_BASE_URL"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        ),
        "qwen": lambda: ChatOpenAI(
            model=kwargs.get("model", "qwen-plus"),
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        ),
    }
    return models[provider]()


if __name__ == "__main__":
    model = get_model("qwen", model="qwen-max")
    response = model.invoke("你是谁？")
    print(response)
