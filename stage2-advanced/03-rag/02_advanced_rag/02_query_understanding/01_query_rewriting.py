"""查询改写（Query Rewriting） — LLM 把口语化查询改成检索友好形式

对应课程章节：二 / 2.3
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)

rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是搜索查询优化专家。将用户的口语化问题改写为适合知识库检索的查询。

【改写规则】
1. 去除口语词（啥、咋、啊、呢）
2. 展开模糊动词（处理→读取/写入/解析）
3. 补充专业术语和同义词
4. 保持简洁，不超过 20 字

【示例】
输入：Python 咋处理 JSON 啊
输出：Python JSON 解析 读取 写入 方法

只输出改写后的查询，无需解释。""",
        ),
        ("human", "{question}"),
    ]
)

rewrite_chain = rewrite_prompt | llm


def rewrite_query(question: str) -> str:
    result = rewrite_chain.invoke({"question": question})
    return result.content.strip()


if __name__ == "__main__":
    user_question = "Python 咋处理 JSON 啊"
    rewritten = rewrite_query(user_question)
    print(f"原始查询: {user_question}")
    print(f"改写后:  {rewritten}")
    # 集成到 RAG：把 rewritten 喂给 retriever.invoke(rewritten) 即可
