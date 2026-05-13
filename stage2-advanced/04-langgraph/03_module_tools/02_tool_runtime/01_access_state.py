"""ToolRuntime — 在工具内访问 state（会话状态）

对应课程章节：模块三 / 1.2.2
"""

from langchain.tools import ToolRuntime, tool


@tool
def summarize_conversation(runtime: ToolRuntime) -> str:
    """总结当前对话内容"""
    messages = runtime.state["messages"]
    human_msgs = sum(1 for m in messages if m.__class__.__name__ == "HumanMessage")
    ai_msgs = sum(1 for m in messages if m.__class__.__name__ == "AIMessage")
    return f"对话包含 {human_msgs} 条用户消息，{ai_msgs} 条 AI 回复"


@tool
def get_user_preference(pref_name: str, runtime: ToolRuntime) -> str:
    """获取自定义用户偏好设置"""
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "未设置")
