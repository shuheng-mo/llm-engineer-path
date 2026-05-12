"""实战：多语言翻译器 — 类封装 + Few-shot + 流式翻译

对应课程章节：第四章 / 5.1
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class MultilingualTranslator:
    SUPPORTED_LANGUAGES = {
        "zh": "中文",
        "en": "英文",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
    }

    EXAMPLES = {
        ("en", "zh"): [
            {"source": "Hello, how are you?", "target": "你好，你好吗？"},
            {"source": "Thank you very much!", "target": "非常感谢！"},
        ],
        ("zh", "en"): [
            {"source": "今天天气真好", "target": "The weather is really nice today"},
            {"source": "我很高兴认识你", "target": "I'm glad to meet you"},
        ],
        ("en", "ja"): [
            {"source": "Good morning", "target": "おはようございます"},
            {"source": "Nice to meet you", "target": "はじめまして"},
        ],
    }

    def __init__(self, model_name: str = "gpt-4o"):
        self.model = ChatOpenAI(model=model_name, temperature=0.3)

    def _get_examples(self, source_lang: str, target_lang: str) -> list:
        return self.EXAMPLES.get((source_lang, target_lang), [])

    def _create_prompt(self, source_lang: str, target_lang: str) -> ChatPromptTemplate:
        source_name = self.SUPPORTED_LANGUAGES[source_lang]
        target_name = self.SUPPORTED_LANGUAGES[target_lang]

        system_message = f"""你是一位专业的翻译专家，精通多种语言。

任务：将{source_name}文本翻译成{target_name}

翻译原则：
1. 准确传达原文含义
2. 保持原文的语气和风格
3. 使用地道的目标语言表达
4. 对于专有名词，保留原文或添加注释
5. 如果原文有错误，先翻译再指出问题"""

        messages = [("system", system_message)]
        for ex in self._get_examples(source_lang, target_lang):
            messages.append(("human", ex["source"]))
            messages.append(("ai", ex["target"]))
        messages.append(("human", "{text}"))

        return ChatPromptTemplate.from_messages(messages)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的源语言: {source_lang}")
        if target_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的目标语言: {target_lang}")

        prompt = self._create_prompt(source_lang, target_lang)
        messages = prompt.format_messages(text=text)
        return self.model.invoke(messages).content

    def translate_stream(self, text: str, source_lang: str, target_lang: str):
        prompt = self._create_prompt(source_lang, target_lang)
        messages = prompt.format_messages(text=text)
        for chunk in self.model.stream(messages):
            yield chunk.content


if __name__ == "__main__":
    translator = MultilingualTranslator()

    result = translator.translate(
        "Artificial intelligence is transforming the world.",
        source_lang="en",
        target_lang="zh",
    )
    print(f"翻译结果: {result}")

    print("\n流式翻译: ", end="")
    for chunk in translator.translate_stream(
        "机器学习是人工智能的一个重要分支。",
        source_lang="zh",
        target_lang="en",
    ):
        print(chunk, end="", flush=True)
    print()
