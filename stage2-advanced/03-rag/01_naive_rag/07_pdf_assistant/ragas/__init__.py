"""Ragas evaluation submodule for the PDF Reading Assistant.

文件组织：
    01_ragas_basics.py    — Faithfulness + Answer Relevancy 双指标演示（最小例子）
    02_ragas_metrics.py   — Context Precision + Context Recall 双指标演示（需要 reference）
    rag_evaluator.py      — 四大指标封装成可复用类
    test_dataset.json     — 测试问答集（包含 user_input + reference 标准答案）
    run_evaluation.py     — 端到端入口：对接 PDFReadingAssistant + 跑批量评估 + 出报告

参考阅读：本目录上一级的 RAGAS_GUIDE.md
"""
