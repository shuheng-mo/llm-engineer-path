"""模板复用与组合 — 继承、Partial、组合多片段

对应课程章节：第四章 / 1.4
"""

from langchain_core.prompts import PromptTemplate

# === 模板继承与扩展 ===
base_template = PromptTemplate.from_template("你是一位{role}。\n\n{instruction}")

translator_template = base_template.partial(
    role="专业翻译官",
    instruction="请将用户提供的文本翻译成目标语言，保持原文的语气和风格。",
)


# === 模板组合 ===
role_template = "你是一位{role}。"
context_template = "背景信息：{context}"
task_template = "任务：{task}"
output_template = "请按以下格式输出：{output_format}"

full_template = PromptTemplate.from_template(
    f"{role_template}\n\n{context_template}\n\n{task_template}\n\n{output_template}"
)

prompt = full_template.format(
    role="数据分析师",
    context="公司本季度销售数据已上传",
    task="分析销售趋势并给出建议",
    output_format="1. 趋势分析 2. 关键发现 3. 改进建议",
)
print(prompt)
