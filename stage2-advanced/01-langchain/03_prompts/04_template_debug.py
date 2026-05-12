"""调试与测试 — input_variables 校验、格式化结果检查

对应课程章节：第四章 / 1.5
"""

from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template("Hello, {name}! Welcome to {place}.")

print(f"所需变量: {template.input_variables}")

# 缺少变量会报 KeyError
try:
    template.format(name="Alice")
except KeyError as e:
    print(f"缺少变量: {e}")

prompt = template.format(name="Alice", place="LangChain World")
print(prompt)


# === 调试技巧：打印模板结构 ===
template = PromptTemplate.from_template("""
你是一位{role}。

用户输入：{user_input}

请根据以上信息，{instruction}
""")

print("=== 模板信息 ===")
print(f"输入变量: {template.input_variables}")
print(f"模板内容:\n{template.template}")

test_prompt = template.format(
    role="客服代表",
    user_input="我的订单什么时候到？",
    instruction="礼貌地回答用户的问题",
)
print(f"\n=== 格式化结果 ===\n{test_prompt}")
