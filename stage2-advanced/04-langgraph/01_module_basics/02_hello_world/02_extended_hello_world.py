"""扩展 Hello World — 写手 → 编辑员 串行流水线

对应课程章节：模块一 / 4.5 实践练习
"""

import pathlib
import sys
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

sys.path.insert(
    0, str(next(p for p in pathlib.Path(__file__).resolve().parents if p.name == "04-langgraph"))
)
from _common import get_chat_model  # noqa: E402

llm = get_chat_model("qwen-max", temperature=0.7)


class AgentState(TypedDict):
    topic: str
    draft: str
    final_post: str


def write_draft(state: AgentState) -> AgentState:
    topic = state["topic"]
    print(f"\n--- [Node 1] 正在为 '{topic}' 撰写初稿 ---")

    response = llm.invoke(
        [
            SystemMessage(
                content="你是一个社交媒体助手。请根据用户的话题，写一段简单的描述，不要加表情包，50字以内。"
            ),
            HumanMessage(content=topic),
        ]
    )
    return {"draft": response.content}


def polish_post(state: AgentState) -> AgentState:
    draft_text = state["draft"]
    print(f"--- [Node 2] 正在润色初稿: {draft_text[:20]}... ---")

    response = llm.invoke(
        [
            SystemMessage(
                content="你是一个爆款文案专家。请将用户的文字改写得更有吸引力，添加3个Emoji，并加上2个Hashtag。"
            ),
            HumanMessage(content=draft_text),
        ]
    )
    return {"final_post": response.content}


builder = StateGraph(AgentState)
builder.add_node("writer", write_draft)
builder.add_node("editor", polish_post)
builder.add_edge(START, "writer")
builder.add_edge("writer", "editor")
builder.add_edge("editor", END)

graph = builder.compile()


if __name__ == "__main__":
    user_topic = "周五下班去吃火锅"
    print(f"=== 开始生成文案: {user_topic} ===")
    result = graph.invoke({"topic": user_topic})
    print("\n" + "=" * 30)
    print("FINAL OUTPUT (最终文案)")
    print("=" * 30)
    print(result["final_post"])
