"""6.3 yield 实现依赖 — 同步生成器原理"""

from typing import Generator


# 同步生成器：模拟给资源+清资源
def get_sync_conn() -> Generator[str, None, None]:
    print("1. 创建同步数据库连接（给资源）")
    conn = "同步连接对象"
    yield conn  # 暂停，把连接交给调用方
    print("2. 关闭同步数据库连接（清资源）")  # 再次唤醒才执行


# 原生调用：必须手动写next()，否则代码不执行
gen = get_sync_conn()  # 仅创建生成器对象，无任何打印
res1 = next(gen)  # 第一次唤醒：执行到yield，打印1，拿到连接
print(f"调用方：拿到{res1}，开始用...")
# 调用方用完资源，必须再次next()触发清理
try:
    next(gen)  # 第二次唤醒：执行yield后代码，打印2
except StopIteration:  # 执行完必触发此异常，正常现象
    print("end")
