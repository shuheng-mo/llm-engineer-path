"""条件插入消息 — 根据 flag 动态构建 Prompt + 工厂模式

对应课程章节：第四章 / 2.5
"""
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate


# === 简单条件函数 ===
def create_prompt(include_examples: bool = False, language: str = "中文"):
    messages = [
        ("system", f"你是一位专业的翻译官，请把下面的文本翻译成{language}"),
    ]
    if include_examples:
        messages.extend([
            ("human", "Hello World!"),
            ("ai", "你好，世界！"),
            ("human", "Good afternoon!"),
            ("ai", "下午好！"),
        ])
    messages.append(("human", "{text}"))
    return ChatPromptTemplate.from_messages(messages)


simple_prompt = create_prompt(include_examples=False)
print("简单模板变量:", simple_prompt.input_variables)

example_prompt = create_prompt(include_examples=True)
messages = example_prompt.format_messages(text="How are you?")
print(f"带示例模板消息数: {len(messages)}")


# === 工厂类（Builder 模式） ===
class PromptBuilder:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.examples: List[tuple] = []
        self.context: Optional[str] = None

    def add_example(self, human: str, ai: str):
        self.examples.append(("human", human))
        self.examples.append(("ai", ai))
        return self

    def set_context(self, context: str):
        self.context = context
        return self

    def build(self) -> ChatPromptTemplate:
        messages = [("system", self.system_prompt)]
        if self.context:
            messages.append(("system", f"参考上下文：{self.context}"))
        messages.extend(self.examples)
        messages.append(("human", "{user_input}"))
        return ChatPromptTemplate.from_messages(messages)


builder = PromptBuilder("你是一位 Python 编程专家。")
template = (
    builder
    .add_example("如何创建列表？", "使用方括号：my_list = [1, 2, 3]")
    .add_example("如何遍历列表？", "使用 for 循环：for item in my_list:")
    .set_context("用户是编程初学者")
    .build()
)

messages = template.format_messages(user_input="如何向列表添加元素？")
for message in messages:
    print(f"{message.type}: {message.content}")
