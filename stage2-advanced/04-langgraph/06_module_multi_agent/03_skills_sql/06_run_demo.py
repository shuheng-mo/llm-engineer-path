"""Skills — Step 6：测试 SQL 助手

对应课程章节：模块六 / 四 / Step 6
"""

import uuid

# from .05_create_agent import agent

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

result = agent.invoke(  # noqa: F821
    {
        "messages": [
            {
                "role": "user",
                "content": "写一个SQL查询，找出上个月订单金额超过$1000的所有客户",
            }
        ],
    },
    config,
)

for message in result["messages"]:
    if hasattr(message, "pretty_print"):
        message.pretty_print()
