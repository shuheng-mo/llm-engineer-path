"""变量插值 — 单/多变量、Partial、函数动态填充

对应课程章节：第四章 / 1.3
"""
import datetime
import time

from langchain_core.prompts import PromptTemplate

# === 单变量 / 多变量 ===
simple_template = PromptTemplate.from_template("你好，{name}！")
print(simple_template.format(name="小明"))

multi_template = PromptTemplate.from_template("我是{name}，今年{age}岁，来自{city}。")
print(multi_template.format(name="小明", age=25, city="北京"))


# === Partial 部分变量填充 ===
template = PromptTemplate.from_template("系统时间： {time}\n 用户问题： {question}")
partial_template = template.partial(time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(partial_template.format(question="现在是几点了？"))

time.sleep(3)
print(partial_template.format(question="再问一次 现在是几点了？"))   # time 不会变


# === 用函数动态生成变量值 ===
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


template = PromptTemplate(
    input_variables=["question"],
    partial_variables={"time": get_current_time},
    template="当前时间：{time}\n 用户问题： {question}",
)
print(template.format(question="现在是几点了？"))
time.sleep(3)
print(template.format(question="再问一次 现在是几点了？"))           # time 会变
