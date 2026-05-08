"""BaseChatMessageHistory + InMemoryChatMessageHistory 基础

对应课程章节：第七章 / 3.1
"""
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

# BaseChatMessageHistory 提供：
#   - add_message(message)
#   - add_messages(messages)
#   - clear()
#   - messages

history = InMemoryChatMessageHistory()
history.add_message(HumanMessage(content="你好，我叫小明"))
history.add_message(AIMessage(content="你好小明！很高兴认识你。"))
history.add_message(HumanMessage(content="我是一名程序员"))
history.add_message(AIMessage(content="很棒！程序员是一个很有创造力的职业。"))

for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
