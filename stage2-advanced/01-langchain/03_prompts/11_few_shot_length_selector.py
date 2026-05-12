"""动态选择示例 — LengthBasedExampleSelector（按总长度自动减少示例）

对应课程章节：第四章 / 3.3 长度选择器
"""

import os

from dotenv import load_dotenv
from langchain_core.example_selectors import LengthBasedExampleSelector
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
)

examples = [
    {"input": "happy", "output": "sad"},
    {"input": "tall", "output": "short"},
    {"input": "energetic", "output": "lethargic"},
    {"input": "sunny", "output": "gloomy"},
]

# 必填：告诉选择器如何把示例字典转成文本（用于计算长度）
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input: {input}\nOutput: {output}",
)

example_selector = LengthBasedExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    input_variables=["input"],
    max_length=20,  # 输入超过 20 字符就减少示例
)

print("原始示例：", example_selector.select_examples({"input": "happy"}))
print(">>> 超长输入 - 示例会减少：")
print(example_selector.select_examples({"input": "happy " * 10}))


# 组装 FewShot Chat 模板
chat_example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_selector=example_selector,
    example_prompt=chat_example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请根据示例，给出输入单词的反义词"),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)

prompt_messages = final_prompt.format_messages(input="big")
response = model.invoke(prompt_messages)
print("\n>>> 模型回复：")
print(response.content)
