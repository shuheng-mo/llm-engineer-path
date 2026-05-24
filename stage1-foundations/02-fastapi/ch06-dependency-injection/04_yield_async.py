"""6.3 yield 实现依赖 — 异步生成器原理"""

from typing import AsyncGenerator
import asyncio


# 异步生成器：模拟给异步资源+清资源（FastAPI最常用）
async def get_async_conn() -> (
    AsyncGenerator[str, None]
):  # yield产出的值的类型，生成器最终的返回值类型。
    print("1. 创建异步数据库连接（给资源）")
    conn = "异步连接对象"
    yield conn  # 暂停，把连接交给调用方
    print("2. 关闭异步数据库连接（清资源）")  # 再次唤醒才执行


# 异步代码必须在异步函数中运行
async def main():
    gen = get_async_conn()  # 仅创建异步生成器对象，无打印
    res1 = await gen.__anext__()  # 第一次唤醒：await+__anext__()
    print(f"调用方：拿到{res1}，开始用...")
    # 再次唤醒触发清理
    try:
        await gen.__anext__()  # 第二次唤醒：执行yield后代码
    except StopAsyncIteration:
        print("end")


# 运行异步主函数
asyncio.run(main())
