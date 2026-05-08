"""Subagents — Step 5：运行示例（单领域 + 复杂多领域）

对应课程章节：模块六 / 二 / Step 5
"""
from langchain_core.messages import HumanMessage

# from .04_supervisor import supervisor

print("=== 简单请求 ===")
result = supervisor.invoke({                                          # noqa: F821
    "messages": [HumanMessage(content="上架一款新的蓝牙耳机，价格199元，库存500件")],
})
print(result["messages"][-1].content)


print("\n=== 复杂请求 ===")
result = supervisor.invoke({                                          # noqa: F821
    "messages": [HumanMessage(content="""
        上架夏季新款防晒衣（价格159元，库存1000件），
        同时创建一个"清凉一夏"满199减20的促销活动
    """)],
})
print(result["messages"][-1].content)
