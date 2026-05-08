"""复杂链路调试 — 用 run_name 给节点起名 + indent 缩进打印

对应课程章节：第六章 / 4.6
"""
import asyncio
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name = os.getenv("DASHSCOPE_MODEL_NAME") or "qwen-max"

model = ChatOpenAI(api_key=api_key, base_url=base_url, model=model_name, temperature=0)
parser = StrOutputParser()


# 预处理
preprocess = RunnableLambda(
    lambda x: {"text": x["text"].strip()}
).with_config(run_name="Preprocess")


# 总结
summary_prompt = ChatPromptTemplate.from_template("请用中文总结下面这段文本的要点：\n\n{text}")
summary_chain = (summary_prompt | model | parser).with_config(run_name="SummaryChain")


# 翻译
translation_prompt = ChatPromptTemplate.from_template("请将下面这段文本翻译成英文：\n\n{text}")
translation_chain = (translation_prompt | model | parser).with_config(run_name="TranslationChain")


def combine_result(result: dict) -> str:
    summary = result.get("summary", "")
    translation = result.get("translation", "")
    return (
        "=== 总结 ===\n"
        f"{summary}\n\n"
        "=== 英文翻译 ===\n"
        f"{translation}"
    )


postprocess = RunnableLambda(combine_result).with_config(run_name="Postprocess")


parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "translation": translation_chain,
}).with_config(run_name="ParallelProcessor")

full_chain = preprocess | parallel_chain | postprocess


async def debug_complex_chain():
    test_input = {
        "text": "人工智能（AI）是一门研究如何让机器表现出智能行为的学科，"
                "包括机器学习、自然语言处理、计算机视觉等多个领域。",
    }

    print("输入文本：", test_input["text"], "\n")

    async for event in full_chain.astream_events(test_input, version="v2"):
        kind = event["event"]
        name = event.get("name", "unknown")
        parents = event.get("parent_ids", [])
        indent = "  " * len(parents)

        if kind.endswith("_start"):
            print(f"{indent}→ {name} 开始")
        elif kind.endswith("_end"):
            print(f"{indent}← {name} 结束")

    print("\n==== 最终结果 ====")
    final_result = await full_chain.ainvoke(test_input)
    print(final_result)


if __name__ == "__main__":
    asyncio.run(debug_complex_chain())
