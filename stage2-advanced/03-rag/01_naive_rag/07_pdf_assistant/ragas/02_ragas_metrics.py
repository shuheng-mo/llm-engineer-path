"""Ragas 进阶：Context Precision + Context Recall 双指标演示（评检索器质量）

对应课程章节：第三部分 3.3 + 3.4

关键区别：
    Faithfulness / AnswerRelevancy 评的是「生成阶段」—— 不需要 reference
    Context Precision / Context Recall 评的是「检索阶段」—— **必须有 reference**

reference 是什么？
    人工标注的"标准答案"。用来判断检索回来的 chunk 是不是 reference 的相关支撑。
"""
import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas import SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextPrecision, ContextRecall

load_dotenv()


async def main():
    client = AsyncOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
    )
    llm = llm_factory("qwen-plus", provider="openai", client=client)
    print("✅ 评判用 LLM 初始化成功")

    # ============================================================
    # 一、Context Precision（精确率）—— 解决「检索噪音」
    # ============================================================
    # 原理：判断 retrieved_contexts 里每个 chunk 是否对回答 user_input 有帮助
    #      （用 reference 当判断依据），有用的 chunk 占比 = Precision。
    # 关心的是："检索回来的东西有多少是有用的？"
    sample_noisy = SingleTurnSample(
        user_input="退款政策是什么？",
        reference="用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        retrieved_contexts=[
            "配送政策：全国大部分地区支持包邮，下单后 3-5 个工作日送达。",   # 噪音
            "会员政策：会员可享 9 折优惠，生日月双倍积分。",                  # 噪音
            "退款政策：所有用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",  # 有用
        ],
    )

    sample_clean = SingleTurnSample(
        user_input="退款政策是什么？",
        reference="用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        retrieved_contexts=[
            "退款政策：所有用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        ],
    )

    prec_scorer = ContextPrecision(llm=llm)
    score_noisy = await prec_scorer.ascore(
        user_input=sample_noisy.user_input,
        reference=sample_noisy.reference,
        retrieved_contexts=sample_noisy.retrieved_contexts,
    )
    score_clean = await prec_scorer.ascore(
        user_input=sample_clean.user_input,
        reference=sample_clean.reference,
        retrieved_contexts=sample_clean.retrieved_contexts,
    )

    print("\n" + "=" * 50)
    print("📊 Context Precision 测试结果")
    print("=" * 50)
    print(f"有噪音（3 个 chunk 只 1 个有用）: {score_noisy.value:.3f}")
    print(f"无噪音（1 个 chunk 全有用）     : {score_clean.value:.3f}")

    # ============================================================
    # 二、Context Recall（召回率）—— 解决「检索漏检」
    # ============================================================
    # 原理：拆 reference 成多个 fact（事实点），判断每个 fact 能不能在 retrieved_contexts
    #      里找到支撑。被支撑的 fact 占比 = Recall。
    # 关心的是："标准答案里的关键信息有多少被检索到了？"
    sample_low_recall = SingleTurnSample(
        user_input="退款政策是什么？",
        reference="用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        retrieved_contexts=[
            "退款政策：所有用户可在购买后 30 天内申请退款。",  # 只覆盖了"30 天内退款"，丢了"全额/无需说明/订单号"
        ],
    )

    sample_full_recall = SingleTurnSample(
        user_input="退款政策是什么？",
        reference="用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        retrieved_contexts=[
            "退款政策：所有用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        ],
    )

    recall_scorer = ContextRecall(llm=llm)
    score_low = await recall_scorer.ascore(
        user_input=sample_low_recall.user_input,
        reference=sample_low_recall.reference,
        retrieved_contexts=sample_low_recall.retrieved_contexts,
    )
    score_full = await recall_scorer.ascore(
        user_input=sample_full_recall.user_input,
        reference=sample_full_recall.reference,
        retrieved_contexts=sample_full_recall.retrieved_contexts,
    )

    print("\n" + "=" * 50)
    print("📊 Context Recall 测试结果")
    print("=" * 50)
    print(f"召回不全（丢了关键事实）: {score_low.value:.3f}")
    print(f"召回完全               : {score_full.value:.3f}")

    print("\n💡 解读：")
    print("  Precision 低 → 检索器召回了太多无关 chunk → 调小 k / 提高 lambda_mult / 加 reranker")
    print("  Recall 低     → 关键信息没被检索到 → 加大 k 和 fetch_k / 调小 chunk_size / 用混合检索")


if __name__ == "__main__":
    asyncio.run(main())
