"""Ragas 入门：Faithfulness（忠实度）+ AnswerRelevancy（回答相关性）双指标演示

对应课程章节：第三部分 3.1 + 3.2

学习目标：
    - 学会构造 SingleTurnSample
    - 跑通新版（Ragas 0.4+）的 ascore() 接口
    - 理解两个指标的物理含义和取值

依赖：
    uv pip install ragas openai pandas tabulate
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Ragas 0.4+ 新版 API：所有指标从 ragas.metrics.collections 导入
from ragas import SingleTurnSample
from ragas.embeddings.base import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import AnswerRelevancy, Faithfulness

load_dotenv()


async def main():
    # Step 1：异步 OpenAI 客户端（接 DashScope 兼容模式）
    client = AsyncOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
    )

    # Step 2：评判用 LLM + Embedding
    #   - Faithfulness 只需要 LLM
    #   - AnswerRelevancy 需要 LLM + Embedding（用向量相似度算"问题-反推问题"的距离）
    llm = llm_factory("qwen-plus", provider="openai", client=client)
    embeddings = embedding_factory(
        "openai",
        model="text-embedding-v3",
        client=client,
        interface="modern",
    )
    print("✅ 评判用 LLM 和 Embedding 初始化成功")

    # ============================================================
    # 一、Faithfulness（忠实度）—— 解决幻觉问题
    # ============================================================
    # 原理：把 response 拆成多个 "claim（断言）"，对每个 claim 在 retrieved_contexts
    # 里找证据。能找到证据的 claim 占比 = Faithfulness 分数。
    # 不需要 reference（标准答案），只看"回答里的每句话能不能从文档里找到依据"。
    sample_good = SingleTurnSample(
        user_input="退款政策是什么？",
        response="购买后 30 天内可申请无理由全额退款，只需提供订单号。",
        retrieved_contexts=[
            "退款政策：所有用户可在购买后 30 天内申请全额退款，无需说明原因，提供订单号即可。",
        ],
    )

    # 坏样本：response 里"2 年质保"和"上门维修"在 context 里没有 → 全是幻觉
    sample_bad = SingleTurnSample(
        user_input="产品保修期是多久？",
        response="产品享有 2 年全面质保，包含免费上门维修服务。",
        retrieved_contexts=[
            "质保条款：本产品享有自购买之日起 1 年的质量保证，不包含人为损坏。",
        ],
    )

    faith_scorer = Faithfulness(llm=llm)

    # 新版 API：ascore 直接传字段，不是传 SingleTurnSample 对象
    score_good = await faith_scorer.ascore(
        user_input=sample_good.user_input,
        response=sample_good.response,
        retrieved_contexts=sample_good.retrieved_contexts,
    )
    score_bad = await faith_scorer.ascore(
        user_input=sample_bad.user_input,
        response=sample_bad.response,
        retrieved_contexts=sample_bad.retrieved_contexts,
    )

    print("\n" + "=" * 50)
    print("📊 Faithfulness 测试结果")
    print("=" * 50)
    print(f"无幻觉样本: {score_good.value:.3f}    (应接近 1.0)")
    print(f"有幻觉样本: {score_bad.value:.3f}    (应接近 0.0)")

    # ============================================================
    # 二、Answer Relevancy（回答相关性）—— 解决答非所问
    # ============================================================
    # 原理：让 LLM 从 response "反推"出原问题（生成 N 个候选问题），
    # 然后计算这 N 个问题和 user_input 的 embedding 余弦相似度，取平均。
    # 越相似说明 response 越切题。
    sample_on_topic = SingleTurnSample(
        user_input="退款政策是什么？",
        response="30 天内可无理由退款，需提供订单号。",
        retrieved_contexts=[],  # 这个指标只用 user_input 和 response，contexts 不用
    )

    sample_off_topic = SingleTurnSample(
        user_input="退款政策是什么？",
        response="我们支持全国包邮，下单后 3-5 天即可送达。",
        retrieved_contexts=[],
    )

    sample_partial = SingleTurnSample(
        user_input="退款政策是什么？",
        response=(
            "我们公司成立于 2010 年，主营电子产品，深耕行业 15 年，积累了大量用户口碑。"
            "退款政策是 30 天内无理由退款。"
        ),
        retrieved_contexts=[],
    )

    rel_scorer = AnswerRelevancy(llm=llm, embeddings=embeddings)

    score_on = await rel_scorer.ascore(
        user_input=sample_on_topic.user_input, response=sample_on_topic.response
    )
    score_off = await rel_scorer.ascore(
        user_input=sample_off_topic.user_input, response=sample_off_topic.response
    )
    score_part = await rel_scorer.ascore(
        user_input=sample_partial.user_input, response=sample_partial.response
    )

    print("\n" + "=" * 50)
    print("📊 Answer Relevancy 测试结果")
    print("=" * 50)
    print(f"切题样本     : {score_on.value:.3f}    (应接近 1.0)")
    print(f"完全跑题样本 : {score_off.value:.3f}   (应接近 0.0)")
    print(f"部分跑题样本 : {score_part.value:.3f}  (0.5-0.7，前面铺垫被惩罚)")

    print("\n💡 解读：")
    print("  Faithfulness 越低 → 回答里有 LLM 编造的内容（幻觉）")
    print("  Answer Relevancy 越低 → 回答跑题或铺垫太多无关内容")


if __name__ == "__main__":
    asyncio.run(main())
