"""PromptTemplate 基本用法 — from_template 和显式 input_variables

对应课程章节：第四章 / 1.2
"""
from langchain_core.prompts import PromptTemplate

# 方式 1：from_template
template = PromptTemplate.from_template(
    "请将下面的文本翻译成{target_language}: \n\n{text}"
)
print(template.input_variables)
print(template.format(target_language="英文", text="人工智能正在改变世界"))


# 方式 2：显式指定变量
template = PromptTemplate(
    input_variables=["product", "features"],
    template="请为下面的{product}撰写一段产品描述，主要突出的是以下的特点{features}",
)
print(template.format(product="智能手表", features="健康检测、寻找设备、防水"))
