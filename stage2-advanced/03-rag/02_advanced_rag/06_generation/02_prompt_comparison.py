"""对比无约束 Prompt vs 有约束 Prompt 的回答效果

对应课程章节：二 / 6.1 Prompt 效果对比
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)

context = """
[文档1] 公司年假制度
员工入职满1年，享有5天带薪年假；满3年，享有10天；满5年，享有15天。
年假需提前3天申请，经直属领导批准后生效。
"""

question = "我入职2年了，能休几天年假？另外，年终奖怎么算？"

bad_prompt = f"""
{context}

问题：{question}
"""

good_prompt = f"""
根据以下参考文档回答问题。只使用文档中的信息，如果文档中没有相关内容，请明确说明。

参考文档：
{context}

问题：{question}
"""

print("=" * 60)
print(" 无约束 Prompt 的回答：")
print(llm.invoke(bad_prompt).content)

print("\n" + "=" * 60)
print(" 有约束 Prompt 的回答：")
print(llm.invoke(good_prompt).content)

# 预期：无约束可能编造年终奖（幻觉）；有约束会明确说"文档没有"
