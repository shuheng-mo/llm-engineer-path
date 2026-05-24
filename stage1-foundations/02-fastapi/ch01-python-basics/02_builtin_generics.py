"""1.1 内置类型写法 (list/dict/Optional/Union)"""

a: list[int] = [1, 2, 3]
b: dict[str, int] = {"age": 18}
c: str | None = None  # 等价 Optional[str]
d: int | str = 123  # 等价 Union[int, str]（Python 3.10+）
