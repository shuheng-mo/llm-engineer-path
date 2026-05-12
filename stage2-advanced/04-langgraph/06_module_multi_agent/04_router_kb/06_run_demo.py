"""Router — Step 6：使用路由器（多源知识库一次解决）

对应课程章节：模块六 / 五 / Step 6
"""
# from .05_compile_workflow import workflow

result = workflow.invoke({"query": "如何认证API请求？"})  # noqa: F821

print("原始查询：", result["query"])
print("\n分类：")
for c in result["classifications"]:
    print(f"  {c['source']}: {c['query']}")
print("\n最终答案：")
print(result["final_answer"])
