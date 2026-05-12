"""策略 3：总结消息（Summarize）— 将旧消息压缩为摘要

对应课程章节：模块四 / 4.4
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("QWEN_MODEL_NLP", "qwen-max"),
    base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    api_key=os.getenv("QWEN_API_KEY"),
    temperature=0.3,
)


class State(MessagesState):
    summary: str


def call_model(state: State):
    msgs = state["messages"]
    if state.get("summary"):
        msgs = [SystemMessage(content=f"前情摘要: {state['summary']}")] + msgs
    return {"messages": [model.invoke(msgs)]}


def summarize_node(state: State):
    summary = state.get("summary", "")
    prompt = (
        f"当前摘要：{summary}\n请结合上述新消息更新摘要，保留关键信息(如姓名、喜好等)："
        if summary
        else "请总结上述对话的关键信息："
    )

    new_summary = model.invoke(state["messages"] + [HumanMessage(content=prompt)]).content
    print(f"\n[系统日志] 触发记忆压缩 -> 更新摘要: {new_summary[:30]}...")

    delete_msgs = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": new_summary, "messages": delete_msgs}


def should_summarize(state: State):
    return "summarize" if len(state["messages"]) > 6 else END


workflow = StateGraph(State)
workflow.add_node("chat", call_model)
workflow.add_node("summarize", summarize_node)
workflow.add_edge(START, "chat")
workflow.add_conditional_edges("chat", should_summarize, {"summarize": "summarize", END: END})
workflow.add_edge("summarize", END)

app = workflow.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "qwen_memory_test"}}
    questions = [
        "我叫 Alice，我有一只叫 Luna 的猫。",
        "Luna 喜欢吃金枪鱼罐头。",
        "它今年三岁了。",
        "它最讨厌洗澡。",
        "我的猫叫什么名字？它喜欢吃什么？",
    ]
    for q in questions:
        print(f"\nUser: {q}")
        res = app.invoke({"messages": [HumanMessage(content=q)]}, config)
        print(f"Qwen: {res['messages'][-1].content}")
