"""端到端评估：把 PDFReadingAssistant + RAGEvaluator + 测试集串起来跑出一份完整报告。

对应课程章节：第五部分 5.4 / 5.5

流程：
    1. 初始化 PDFReadingAssistant（加载 PDF + 建向量库）
    2. 初始化 RAGEvaluator
    3. 加载 test_dataset.json
    4. 逐题调用 ask_with_contexts() 收集 (response, retrieved_contexts)
    5. RAGEvaluator 批量评分
    6. 汇总成平均分 + 逐样本明细，写入 evaluation_report.json

使用：
    cd stage2-advanced/03-rag/01_naive_rag/07_pdf_assistant/ragas
    uv run python run_evaluation.py
"""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from ragas import SingleTurnSample

# 当前文件所在目录
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
ENV_FILE = PARENT.parent.parent / ".env"   # stage2-advanced/03-rag/.env
load_dotenv(ENV_FILE, override=False)

# 动态加载 PDFReadingAssistant（因父目录路径 "07_pdf_assistant" 以数字开头无法用 import）
ASSISTANT_FILE = PARENT / "pdf_reading_assistant.py"
spec = importlib.util.spec_from_file_location("pdf_reading_assistant", ASSISTANT_FILE)
_mod = importlib.util.module_from_spec(spec)
sys.modules["pdf_reading_assistant"] = _mod
spec.loader.exec_module(_mod)
PDFReadingAssistant = _mod.PDFReadingAssistant
DATA_DIR = _mod.DATA_DIR

# 当前包的 rag_evaluator（同目录普通 import 即可）
from rag_evaluator import RAGEvaluator   # noqa: E402


def _classify(score: float) -> str:
    if score >= 0.9:
        return "✅ 优秀"
    if score >= 0.7:
        return "⚠️  需优化"
    return "❌ 严重问题"


async def run_full_evaluation():
    print("=" * 70)
    print("🚀 PDF 阅读助手 × Ragas 完整评估开始")
    print("=" * 70)

    # ============================================================
    # Step 1：初始化 PDF 助手（加载 data/ 下所有 PDF）
    # ============================================================
    print("\n📚 Step 1：初始化 PDF 阅读助手...")
    assistant = PDFReadingAssistant(pdf_directory=str(DATA_DIR))

    # ============================================================
    # Step 2：初始化 Ragas 评估器
    # ============================================================
    print("\n🔧 Step 2：初始化 Ragas 评估器...")
    evaluator = RAGEvaluator(model="qwen-plus")

    # ============================================================
    # Step 3：加载测试集
    # ============================================================
    print("\n📋 Step 3：加载测试数据集...")
    with open(HERE / "test_dataset.json", encoding="utf-8") as f:
        test_data = json.load(f)
    print(f"✅ 共加载 {len(test_data)} 个测试案例")

    # ============================================================
    # Step 4：逐题调用助手收集 (answer, retrieved_contexts)
    # ============================================================
    print("\n🔍 Step 4：调用 PDF 助手，收集真实问答数据...")
    samples = []
    for i, item in enumerate(test_data, 1):
        question = item["user_input"]
        reference = item["reference"]
        print(f"  [{i}/{len(test_data)}] {question[:40]}...")
        answer, contexts = assistant.ask_with_contexts(question)
        print(f"     → 检索到 {len(contexts)} 个片段")
        samples.append(SingleTurnSample(
            user_input=question,
            response=answer,
            reference=reference,
            retrieved_contexts=contexts,
        ))

    # 评估时每个问题应当独立，清掉对话历史
    assistant.clear_history()

    # ============================================================
    # Step 5：批量评估
    # ============================================================
    print("\n📊 Step 5：Ragas 评判中（调用 LLM 判卷，要花点时间）...")
    results = await evaluator.evaluate_batch_samples(samples)
    print("✅ 评估完成")

    # ============================================================
    # Step 6：报告输出
    # ============================================================
    print("\n" + "=" * 70)
    print("📈 完整评估报告")
    print("=" * 70)

    f_scores = [r["faithfulness"] for r in results]
    r_scores = [r["answer_relevancy"] for r in results]
    p_scores = [r.get("context_precision", 0) for r in results]
    rc_scores = [r.get("context_recall", 0) for r in results]

    avg_f = sum(f_scores) / len(f_scores)
    avg_r = sum(r_scores) / len(r_scores)
    avg_p = sum(p_scores) / len(p_scores)
    avg_rc = sum(rc_scores) / len(rc_scores)

    print("\n📌 系统整体平均分数：")
    print(f"  忠实度（Faithfulness）        : {avg_f:.3f}  {_classify(avg_f)}")
    print(f"  回答相关性（Answer Relevancy）: {avg_r:.3f}  {_classify(avg_r)}")
    print(f"  上下文精确率（Context Prec.） : {avg_p:.3f}  {_classify(avg_p)}")
    print(f"  上下文召回率（Context Rec.）  : {avg_rc:.3f}  {_classify(avg_rc)}")

    print("\n📋 逐样本详细结果：")
    for sample, result in zip(samples, results):
        print(evaluator.format_result(sample, result))

    # 保存完整报告
    report = {
        "summary": {
            "total_samples": len(samples),
            "average_scores": {
                "faithfulness": round(avg_f, 3),
                "answer_relevancy": round(avg_r, 3),
                "context_precision": round(avg_p, 3),
                "context_recall": round(avg_rc, 3),
            },
        },
        "detailed_results": [
            {
                "question": s.user_input,
                "response": s.response,
                "reference": s.reference,
                "retrieved_contexts": s.retrieved_contexts,
                "scores": r,
            }
            for s, r in zip(samples, results)
        ],
    }

    report_path = HERE / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完整报告已保存到 {report_path}")


if __name__ == "__main__":
    asyncio.run(run_full_evaluation())
