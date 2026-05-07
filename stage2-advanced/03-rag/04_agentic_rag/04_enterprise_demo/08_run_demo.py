"""Demo — 用 stream() 看每一步的状态变化

对应课程章节：四 / 第四章 6.1
"""
# from .07_orchestration import app

inputs = {"question": "特斯拉2023年关于自动驾驶的研发投入是多少？"}

last_value = None
for output in app.stream(inputs):  # noqa: F821
    for key, value in output.items():
        print(f"完成节点: {key}")
        print("------------------")
        last_value = value

if last_value and "generation" in last_value:
    print(f"\n最终答案: {last_value['generation']}")
