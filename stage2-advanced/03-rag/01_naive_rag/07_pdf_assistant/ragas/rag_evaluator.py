"""RAGEvaluator — 把 Ragas 四大指标封装成可复用的类。

对应课程章节：第四部分 4.2

用法：
    evaluator = RAGEvaluator(model="qwen-plus")
    result = await evaluator.evaluate_single_sample(sample)
    # result = {"faithfulness": 0.95, "answer_relevancy": 0.88, ...}

    # 批量：
    results = await evaluator.evaluate_batch_samples([s1, s2, s3])

接口设计要点：
    - 一次性初始化 LLM / Embedding / 四个 scorer，后续重复调用零开销
    - evaluate_single_sample / evaluate_batch_samples 两套并存（批量用 asyncio.gather）
    - format_result 出一个适合打印的字符串
"""
import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas import SingleTurnSample
from ragas.embeddings.base import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

load_dotenv()


class RAGEvaluator:
    """封装四大 Ragas 指标，支持单 / 批量评估。"""

    def __init__(self, model: str = "qwen-plus"):
        self.client = self._init_client()
        self.llm = llm_factory(model=model, provider="openai", client=self.client)
        self.embeddings = embedding_factory(
            "openai",
            model="text-embedding-v3",
            client=self.client,
            interface="modern",
        )
        self.evaluators = {
            "faithfulness": Faithfulness(llm=self.llm),
            "answer_relevancy": AnswerRelevancy(llm=self.llm, embeddings=self.embeddings),
            "context_precision": ContextPrecision(llm=self.llm),
            "context_recall": ContextRecall(llm=self.llm),
        }
        print("✅ RAGEvaluator 初始化完成")

    @staticmethod
    def _init_client() -> AsyncOpenAI:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        if not api_key:
            raise ValueError("❌ 未找到 DASHSCOPE_API_KEY，请检查 .env 配置")
        return AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def evaluate_single_sample(self, sample: SingleTurnSample) -> dict:
        """评估单个样本，返回四大指标分数字典。

        注意：context_precision / context_recall 需要 sample.reference，
        没有 reference 时这两项会被跳过。
        """
        result: dict[str, float] = {}

        # Faithfulness：不需要 reference
        score = await self.evaluators["faithfulness"].ascore(
            user_input=sample.user_input,
            response=sample.response,
            retrieved_contexts=sample.retrieved_contexts,
        )
        result["faithfulness"] = round(score.value, 3)

        # AnswerRelevancy：不需要 reference 也不需要 contexts
        score = await self.evaluators["answer_relevancy"].ascore(
            user_input=sample.user_input,
            response=sample.response,
        )
        result["answer_relevancy"] = round(score.value, 3)

        # Context Precision / Recall：必须有 reference
        if sample.reference:
            score = await self.evaluators["context_precision"].ascore(
                user_input=sample.user_input,
                reference=sample.reference,
                retrieved_contexts=sample.retrieved_contexts,
            )
            result["context_precision"] = round(score.value, 3)

            score = await self.evaluators["context_recall"].ascore(
                user_input=sample.user_input,
                reference=sample.reference,
                retrieved_contexts=sample.retrieved_contexts,
            )
            result["context_recall"] = round(score.value, 3)

        return result

    async def evaluate_batch_samples(self, samples: list[SingleTurnSample]) -> list[dict]:
        """批量评估，asyncio.gather 并发。"""
        return await asyncio.gather(
            *[self.evaluate_single_sample(s) for s in samples]
        )

    @staticmethod
    def format_result(sample: SingleTurnSample, result: dict) -> str:
        """格式化单个样本的评估结果，便于人工查看。"""
        lines = [
            "=" * 60,
            f"📋 问题：{sample.user_input}",
            "=" * 60,
        ]
        if "faithfulness" in result:
            lines.append(f"忠实度（无幻觉）        : {result['faithfulness']:.3f}")
        if "answer_relevancy" in result:
            lines.append(f"回答相关性（不跑题）    : {result['answer_relevancy']:.3f}")
        if "context_precision" in result:
            lines.append(f"上下文精确率（无噪音）  : {result['context_precision']:.3f}")
        if "context_recall" in result:
            lines.append(f"上下文召回率（无漏检）  : {result['context_recall']:.3f}")
        return "\n".join(lines)


# ============================================================
# 自测：直接 `uv run python rag_evaluator.py` 验证封装能跑
# ============================================================
async def _test_evaluator():
    evaluator = RAGEvaluator(model="qwen-plus")

    sample = SingleTurnSample(
        user_input="退款政策是什么？",
        response="购买后 30 天内可申请无理由全额退款，只需提供订单号。",
        reference="用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        retrieved_contexts=[
            "退款政策：所有用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
            "配送政策：全国包邮，3-5 天送达。",  # 加点噪音测 precision
        ],
    )

    result = await evaluator.evaluate_single_sample(sample)
    print(evaluator.format_result(sample, result))


if __name__ == "__main__":
    asyncio.run(_test_evaluator())
