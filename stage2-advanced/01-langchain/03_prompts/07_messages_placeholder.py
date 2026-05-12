"""MessagesPlaceholder — 动态插入历史消息（含 optional）

对应课程章节：第四章 / 2.4
"""

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# === 必填的历史消息 ===
template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个专业的技术顾问"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}"),
    ]
)

history = [
    HumanMessage(content="你好"),
    AIMessage(content="您好 请问有什么可以帮到您？"),
    HumanMessage(content="什么是大模型"),
    AIMessage(content="大模型是....."),
]

messages = template.format_messages(chat_history=history, user_input="他有什么特点呢？")
print(f"总消息数：{len(messages)}")
for message in messages:
    print(f"[{message.type}] {message.content[:50]}...")


# === 可选的历史消息（optional=True） ===
template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是 AI 助手。"),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{input}"),
    ]
)

# 不传 history 也行
messages1 = template.format_messages(input="你好")
print(f"无历史: {len(messages1)} 条消息")

messages2 = template.format_messages(
    input="继续",
    history=[HumanMessage(content="之前的问题"), AIMessage(content="之前的回答")],
)
print(f"有历史: {len(messages2)} 条消息")
