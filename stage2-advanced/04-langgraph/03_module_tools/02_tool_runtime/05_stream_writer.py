"""ToolRuntime — Stream Writer 流式输出工具进度

对应课程章节：模块三 / 1.2.6
"""
from langchain.tools import ToolRuntime, tool


@tool
def process_large_file(filename: str, runtime: ToolRuntime) -> str:
    """处理大文件"""
    writer = runtime.stream_writer

    writer(f"开始读取文件：{filename}")
    # 模拟处理...
    writer("文件读取完成，开始解析...")
    # 模拟解析...
    writer("解析完成，正在生成报告...")

    return f"文件 {filename} 处理完成"
