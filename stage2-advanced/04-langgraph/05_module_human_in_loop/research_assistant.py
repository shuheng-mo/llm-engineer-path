"""研报助手 V4 — interrupt_before + update_state 实现人工审核闭环

对应课程章节：模块五 / 4.1 实战

依赖:
uv pip install tavily-python
"""

"""
研报助手 V4 - 人工审核闭环（单文件完整版）

运行前请设置环境变量：
  export DASHSCOPE_API_KEY=sk-xxx
  export TAVILY_API_KEY=tvly-xxx

流程：
  用户输入主题 → AI 搜索撰写 → 暂停等人工审核
    → 批准 → 发布
    → 修改意见 → AI 重写 → 再次审核 → ...
"""
import pathlib
import sys
import uuid
from typing import Annotated, Literal

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402


# ============================================================
# 1. 状态定义
# ============================================================
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================
# 2. LLM 和工具初始化
# ============================================================
model = get_chat_model("qwen-max", temperature=0.7)

search_tool = TavilySearchResults(max_results=3)
tools = [search_tool]
model_with_tools = model.bind_tools(tools)


# ============================================================
# 3. 节点定义
# ============================================================
def writer_node(state):
    """写手节点：调用带搜索工具的 LLM 进行撰写或重写"""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools=tools)


def human_review_node(state):
    """人工审核占位节点。本身无逻辑，作为 interrupt_before 的挂载点。"""
    return state


def publisher_node(state):
    """发布节点：审核通过后执行（可扩展为存数据库、发邮件等）"""
    print("\n" + "=" * 50)
    print(">>> [系统] 研报已正式发布！已归档并发送邮件。 <<<")
    print("=" * 50 + "\n")
    return {"messages": [AIMessage(content="✅ 研报已正式发布，流程结束。")]}


# ============================================================
# 4. 路由函数
# ============================================================
def should_use_tools(state) -> Literal["tools", "human_review"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "human_review"


def review_router(state) -> Literal["publisher", "writer"]:
    last_message = state["messages"][-1]
    content = last_message.content.lower() if hasattr(last_message, "content") else ""

    approve_keywords = ["批准", "通过", "approve", "ok", "确认", "发布"]
    if any(kw in content for kw in approve_keywords):
        return "publisher"
    return "writer"


# ============================================================
# 5. 构建并编译图
# ============================================================
workflow = StateGraph(State)
workflow.add_node("writer", writer_node)
workflow.add_node("tools", tool_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("publisher", publisher_node)

workflow.add_edge(START, "writer")

workflow.add_conditional_edges(
    "writer",
    should_use_tools,
    {"tools": "tools", "human_review": "human_review"},
)

workflow.add_edge("tools", "writer")
workflow.add_conditional_edges(
    "human_review",
    review_router,
    {"publisher": "publisher", "writer": "writer"},
)
workflow.add_edge("publisher", END)

memory = MemorySaver()
app_v4 = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"],  # 关键：在人工审核节点前暂停
)


# ============================================================
# 6. 辅助函数
# ============================================================
def print_separator(char="─", length=60):
    print(char * length)


def print_ai_response(messages):
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "ai" and msg.content:
            print("\n[AI 草稿]:")
            print_separator()
            print(msg.content)
            print_separator()
            return


# ============================================================
# 7. 主程序入口
# ============================================================
def run():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 60)
    print("  📊 研报助手 V4 - 人工审核版")
    print("=" * 60)

    topic = input("\n请输入研报主题（例：2026年新能源汽车市场分析）: ").strip()
    if not topic:
        topic = "2024年全球AI芯片市场分析"
        print(f"使用默认主题：{topic}")

    initial_prompt = f"""你是一位专业的研究分析师。请针对以下主题撰写一份研究报告草稿。

主题：{topic}

要求：
1. 先使用搜索工具查找最新的相关资料
2. 基于搜索结果，撰写一份结构清晰的研报草稿
3. 研报需包含：摘要、行业背景、市场现状、关键趋势、风险分析、结论与建议
4. 引用数据需标明来源
5. 使用中文撰写

请开始。"""

    print("\n⏳ AI 正在搜索资料并撰写草稿，请稍候...\n")

    for event in app_v4.stream(
        {"messages": [HumanMessage(content=initial_prompt)]},
        config=config,
        stream_mode="values",
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, "type"):
                if last_msg.type == "ai" and getattr(last_msg, "tool_calls", None):
                    for tc in last_msg.tool_calls:
                        print(f"  🔍 正在调用工具: {tc['name']}")
                elif last_msg.type == "tool":
                    print(f"  ✅ 工具返回结果（{len(last_msg.content)} 字符）")

    current_state = app_v4.get_state(config)
    print_ai_response(current_state.values["messages"])

    while True:
        print("\n" + "=" * 60)
        print("  👤 人工审核环节")
        print("=" * 60)
        print("  输入 '批准' / '通过'  → 正式发布")
        print("  输入修改意见           → AI 将根据意见重写")
        print("  输入 'quit'           → 退出程序")
        print_separator()

        user_input = input("\n您的审核意见: ").strip()
        if not user_input:
            print("⚠️  请输入审核意见。")
            continue
        if user_input.lower() == "quit":
            print("\n 已退出程序。")
            return

        # 把审核意见注入 state（human-in-the-loop 的核心）
        app_v4.update_state(config, {"messages": [HumanMessage(content=user_input)]})

        print("\n处理中...\n")
        for event in app_v4.stream(None, config=config, stream_mode="values"):
            if "messages" in event:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, "type"):
                    if last_msg.type == "ai" and getattr(last_msg, "tool_calls", None):
                        for tc in last_msg.tool_calls:
                            print(f"  🔍 正在调用工具: {tc['name']}")
                    elif last_msg.type == "tool":
                        print(f"  ✅ 工具返回结果（{len(last_msg.content)} 字符）")

        current_state = app_v4.get_state(config)
        if current_state.next:
            print_ai_response(current_state.values["messages"])
        else:
            print_ai_response(current_state.values["messages"])
            print("\n流程已完成！")
            return


if __name__ == "__main__":
    run()
