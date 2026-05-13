"""ToolRuntime — Stream Writer 流式输出工具进度

对应课程章节：模块三 / 1.2.6

`runtime.stream_writer(chunk)` 让工具能在执行**过程中**主动往 stream 通道塞
事件，前端立即能看到（典型场景：长任务进度、思考过程、调试信息）。
消费侧：`agent.stream(..., stream_mode="custom")` 才会收到这些 chunk。
"""

import pathlib
import sys
import time

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

model = get_chat_model("qwen-max")


@tool
def process_large_file(filename: str, runtime: ToolRuntime) -> str:
    """处理一个大文件并返回处理结果（演示用，每步有 0.5s 模拟耗时）。"""
    writer = runtime.stream_writer

    writer({"stage": "read", "msg": f"开始读取文件：{filename}"})
    time.sleep(0.5)

    writer({"stage": "parse", "msg": "文件读取完成，开始解析..."})
    time.sleep(0.5)

    writer({"stage": "report", "msg": "解析完成，正在生成报告..."})
    time.sleep(0.5)

    writer({"stage": "done", "msg": f"文件 {filename} 处理完成"})
    return f"文件 {filename} 处理完成，共扫描 12,345 行，发现 3 处异常"


agent = create_agent(
    model=model,
    tools=[process_large_file],
    system_prompt=("你是一个文件处理助手。当用户要求处理文件时，调用 process_large_file 工具。"),
)


if __name__ == "__main__":
    user_input = "帮我处理一下 server.log 这个日志文件"
    print(f"→ user: {user_input}\n")

    # stream_mode="custom" → 只接收 stream_writer 推的事件
    # stream_mode=["custom", "updates"] → 同时拿到工具进度 + 节点更新
    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode=["custom", "updates"],
    ):
        if mode == "custom":
            # 工具用 writer({...}) 推送的进度
            print(f"  [progress] {chunk}")
        elif mode == "updates":
            # 节点级别的 State 更新（model / tools）
            for node, state in chunk.items():
                if "messages" in state and state["messages"]:
                    last = state["messages"][-1]
                    summary = last.content[:60] + "..." if len(last.content) > 60 else last.content
                    print(f"  [{node}] {type(last).__name__}: {summary or '(空，等下一步)'}")
