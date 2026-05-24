"""1.1 Type Hints — 传统写法 vs 现代写法"""


# 传统写法
def get_full_name(first_name, last_name):
    return first_name.title() + " " + last_name.title()


# 现代写法 (Type Hints)
def get_full_name_typed(first_name: str, last_name: str) -> str:  # 返回的是字符串
    # 编辑器知道 first_name 是 str，会自动提示 .title() 方法
    return first_name.title() + " " + last_name.title()
