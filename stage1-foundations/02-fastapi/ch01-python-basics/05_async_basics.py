"""2. 异步编程基础 — 阻塞/非阻塞等待对比"""

import asyncio
import time


async def make_coffee():
    print("开始煮咖啡...")
    # time.sleep(3)
    await asyncio.sleep(3)  # 煮咖啡需要 3 秒
    print("咖啡好了！")


async def make_toast():
    print("开始烤面包...")
    await asyncio.sleep(2)  # 烤面包需要 2 秒
    print("面包好了！")


async def main():
    # 同时开始煮咖啡和烤面包
    await asyncio.gather(make_coffee(), make_toast())
    print("早餐准备完毕！")


asyncio.run(main())
