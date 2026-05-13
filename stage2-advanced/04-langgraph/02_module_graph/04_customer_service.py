"""综合实践：多轮对话客服系统 — MessagesState + Checkpointer + 模拟 DB

对应课程章节：模块二 / 综合实践
"""

import pathlib
import sys
import uuid

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

llm = get_chat_model("qwen-max", temperature=0.7)


class State(MessagesState):
    """使用内置的 MessagesState，自动管理消息历史"""


ORDERS = {
    "ORD001": {"商品": "iPhone 15", "状态": "已发货", "价格": 5999},
    "ORD002": {"商品": "AirPods", "状态": "配送中", "价格": 1299},
}


def customer_service_node(state: State) -> dict:
    system_prompt = """你是智能客服助手。

你的能力：
1. 查询订单：当用户提供订单号（格式：ORD001、ORD002等），从数据库查询订单信息
2. 产品咨询：回答产品相关问题

订单数据库：
- ORD001: iPhone 15, 已发货, ¥5999
- ORD002: AirPods, 配送中, ¥1299

产品信息：
- iPhone 15: ¥5999
- AirPods: ¥1299

处理流程：
1. 如果用户提到"订单"或"查询"，引导用户提供订单号
2. 如果用户提供了订单号（ORD开头），查询并返回订单详情
3. 如果是产品咨询，直接回答
4. 回答要简洁、友好
"""

    messages = state["messages"]
    user_message = messages[-1].content

    order_id = next((w for w in user_message.split() if w.startswith("ORD")), None)
    if order_id and order_id in ORDERS:
        order = ORDERS[order_id]
        response = (
            f"📦 订单详情\n"
            f"━━━━━━━━━━━━━━━\n"
            f"订单号：{order_id}\n"
            f"商品：{order['商品']}\n"
            f"状态：{order['状态']}\n"
            f"价格：¥{order['价格']}\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"还需要其他帮助吗？"
        )
        return {"messages": [AIMessage(content=response)]}

    full_messages = [SystemMessage(content=system_prompt)] + messages
    return {"messages": [llm.invoke(full_messages)]}


def build_graph():
    memory = MemorySaver()
    graph = StateGraph(State)
    graph.add_node("customer_service", customer_service_node)
    graph.add_edge(START, "customer_service")
    graph.add_edge("customer_service", END)
    return graph.compile(checkpointer=memory)


def run_interactive():
    graph = build_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 50)
    print("💬 智能客服系统")
    print("=" * 50)
    print(f"会话 ID: {thread_id[:8]}...\n输入 'quit' 退出\n" + "-" * 50)

    while True:
        try:
            user_input = input("\n👤 您: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit", "q"}:
                print("\n👋 感谢使用，再见！")
                break

            result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
            for msg in result.get("messages", []):
                pass
            last = result["messages"][-1]
            if isinstance(last, AIMessage):
                print(f"\n🤖 {last.content}")

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback

            traceback.print_exc()


def run_auto_test():
    graph = build_graph()
    # !!! 必须传 thread_id
    # thread_id 是 checkpoint 的分桶键。同一个 thread_id 的所有 invoke 共享一条对话历史；不同 thread_id完全隔离。忘了传 thread_id，checkpointer 即使配了也不生效——这是新手最常踩的坑。
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("\n" + "=" * 50)
    print(" 智能客服系统 - 自动测试")
    print("=" * 50)

    for user_input in ["我要查询订单", "ORD001", "iPhone多少钱", "谢谢"]:
        print(f"\n👤 用户: {user_input}")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        last = result["messages"][-1]
        if isinstance(last, AIMessage):
            print(f"\n🤖 {last.content}")

    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    # run_auto_test()
    run_interactive()
