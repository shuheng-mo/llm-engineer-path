"""实战：智能文本处理流水线（预处理 → 4 路并行分析 → 报告整合）

对应课程章节：第六章 / 6.2
"""
import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = os.getenv("DASHSCOPE_MODEL_NAME") or "qwen-max"

model = ChatOpenAI(api_key=api_key, base_url=base_url, model=model_name, temperature=0)


def preprocess_text(text: str) -> dict:
    cleaned = " ".join(text.strip().split())
    return {
        "text": cleaned,
        "original_length": len(text),
        "cleaned_length": len(cleaned),
        "timestamp": datetime.now().isoformat(),
    }


# 摘要
summary_prompt = ChatPromptTemplate.from_template("请用50字以内总结以下文本的核心内容：\n\n{text}")
summary_chain = (lambda x: {"text": x["text"]}) | summary_prompt | model | StrOutputParser()

# 关键词
keywords_prompt = ChatPromptTemplate.from_template(
    """提取以下文本的5个关键词，以JSON数组格式返回：

文本：{text}

只返回JSON数组，格式如：["关键词1", "关键词2", ...]"""
)
keywords_chain = (lambda x: {"text": x["text"]}) | keywords_prompt | model | JsonOutputParser()

# 情感分析
sentiment_prompt = ChatPromptTemplate.from_template(
    """分析以下文本的情感倾向，返回JSON格式：
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "reason": "简要说明原因"
}}

文本：{text}"""
)
sentiment_chain = (lambda x: {"text": x["text"]}) | sentiment_prompt | model | JsonOutputParser()

# 语言检测
language_prompt = ChatPromptTemplate.from_template(
    """检测以下文本的语言，返回JSON格式：
{{
    "language": "语言名称",
    "code": "语言代码（如zh、en）",
    "confidence": 0.0-1.0
}}

文本：{text}"""
)
language_chain = (lambda x: {"text": x["text"]}) | language_prompt | model | JsonOutputParser()


parallel_analysis = RunnableParallel({
    "summary": summary_chain,
    "keywords": keywords_chain,
    "sentiment": sentiment_chain,
    "language": language_chain,
    "metadata": RunnablePassthrough(),
})


def format_report(analysis_results: dict) -> dict:
    return {
        "report": {
            "generated_at": datetime.now().isoformat(),
            "text_info": {
                "original_length": analysis_results["metadata"]["original_length"],
                "cleaned_length": analysis_results["metadata"]["cleaned_length"],
            },
            "analysis": {
                "summary": analysis_results["summary"],
                "keywords": analysis_results["keywords"],
                "sentiment": analysis_results["sentiment"],
                "language": analysis_results["language"],
            },
        }
    }


text_analysis_pipeline = (
    RunnableLambda(preprocess_text)
    | parallel_analysis
    | RunnableLambda(format_report)
).with_config(run_name="TextAnalysisPipeline")


async def main():
    sample_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
    它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    近年来，随着深度学习技术的突破，AI在图像识别、自然语言处理、游戏对弈等领域
    取得了显著成就，正在深刻改变着人类的生活和工作方式。
    """

    print("=" * 60)
    print("开始文本分析...")
    print("=" * 60)

    async for event in text_analysis_pipeline.astream_events(sample_text, version="v2"):
        if event["event"] == "on_chain_start":
            print(f"▶ 开始: {event.get('name', 'unknown')}")
        elif event["event"] == "on_chain_end" and event.get("name") == "TextAnalysisPipeline":
            result = event["data"]["output"]
            print("\n" + "=" * 60)
            print("分析报告")
            print("=" * 60)
            report = result["report"]
            print(f"\n📊 文本信息: 原始 {report['text_info']['original_length']} / 清理后 {report['text_info']['cleaned_length']}")
            print(f"\n📝 摘要: {report['analysis']['summary']}")
            print(f"\n🏷️ 关键词: {', '.join(report['analysis']['keywords'])}")
            sentiment = report["analysis"]["sentiment"]
            print(f"\n😊 情感分析: {sentiment['sentiment']} ({sentiment['confidence']}) - {sentiment['reason']}")
            lang = report["analysis"]["language"]
            print(f"\n🌍 语言: {lang['language']} ({lang['code']}) - {lang['confidence']}")


if __name__ == "__main__":
    asyncio.run(main())
