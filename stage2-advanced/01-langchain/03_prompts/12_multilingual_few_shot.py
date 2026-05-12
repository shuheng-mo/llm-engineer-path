"""多语言 Few-shot — 按目标语言切换示例库

对应课程章节：第四章 / 3.4
"""

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

multilingual_examples = {
    "zh": [
        {"input": "Hello", "output": "你好"},
        {"input": "Thank you", "output": "谢谢"},
        {"input": "Goodbye", "output": "再见"},
    ],
    "ja": [
        {"input": "Hello", "output": "こんにちは"},
        {"input": "Thank you", "output": "ありがとう"},
        {"input": "Goodbye", "output": "さようなら"},
    ],
    "ko": [
        {"input": "Hello", "output": "안녕하세요"},
        {"input": "Thank you", "output": "감사합니다"},
        {"input": "Goodbye", "output": "안녕히 가세요"},
    ],
}


def create_translation_prompt(target_lang: str) -> ChatPromptTemplate:
    lang_names = {"zh": "中文", "ja": "日语", "ko": "韩语"}
    examples = multilingual_examples.get(target_lang, [])

    example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", f"你是一位专业翻译，请将英文翻译成{lang_names[target_lang]}。"),
            few_shot_prompt,
            ("human", "{text}"),
        ]
    )


zh_prompt = create_translation_prompt("zh")
messages = zh_prompt.format_messages(text="Good morning")
for m in messages:
    print(f"[{m.type}] {m.content}")
