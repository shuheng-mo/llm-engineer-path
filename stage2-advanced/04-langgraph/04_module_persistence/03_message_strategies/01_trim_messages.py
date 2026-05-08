"""策略 1：修剪消息（Trim Messages）— 保留最近 N 个 token

对应课程章节：模块四 / 4.2
"""
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

model = ChatOpenAI(model="gpt-4o-mini")


def call_model_with_trimming(state: MessagesState):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=100,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )
    print(f"Debug: 实际发送给模型的消息数: {len(trimmed_messages)}")
    response = model.invoke(trimmed_messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("bot", call_model_with_trimming)
builder.add_edge(START, "bot")
builder.add_edge("bot", END)
graph = builder.compile()
