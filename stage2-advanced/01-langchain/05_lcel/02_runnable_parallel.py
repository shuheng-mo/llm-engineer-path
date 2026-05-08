"""RunnableParallel（RunnableMap） — 并行处理多个分支

对应课程章节：第六章 / 3.3
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

summary_chain = ChatPromptTemplate.from_template("请用一句话总结：{text}") | model
keywords_chain = ChatPromptTemplate.from_template("请提取3个关键词：{text}") | model
sentiment_chain = ChatPromptTemplate.from_template("请分析情感倾向（正面/负面/中性）：{text}") | model

parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "keywords": keywords_chain,
    "sentiment": sentiment_chain,
})

result = parallel_chain.invoke({
    "text": "今天天气真好，阳光明媚，我和朋友去公园野餐，度过了美好的一天。",
})

print(result["summary"].content)
print(result["keywords"].content)
print(result["sentiment"].content)
