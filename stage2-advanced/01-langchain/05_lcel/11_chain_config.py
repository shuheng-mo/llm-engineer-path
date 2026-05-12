"""RunnableConfig — 给链加 run_name / tags / metadata / max_concurrency

对应课程章节：第六章 / 5.4
"""

from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    run_name="我的AI助手",
    tags=["production", "v1"],
    metadata={"user_id": "12345"},
    max_concurrency=5,
    callbacks=[],
)

# result = chain.invoke({"topic": "AI"}, config=config)     # noqa: F821
