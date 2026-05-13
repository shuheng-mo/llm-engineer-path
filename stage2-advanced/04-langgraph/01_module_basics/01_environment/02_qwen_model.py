"""千问模型基础调用（ChatTongyi）

对应课程章节：模块一 / 3.3

注：底层 ChatTongyi 实例化逻辑已抽到 04-langgraph/_common.py
"""

import pathlib
import sys

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

llm = get_chat_model("qwen-max", temperature=0.7, top_p=0.9)

if __name__ == "__main__":
    response = llm.invoke("你好，请介绍一下 LangGraph")
    print(response.content)
