"""在 Prompt 中使用结构化长期记忆 — 个性化对话链

对应课程章节：第七章 / 5.4
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# from .09_user_profile_pydantic import UserProfile


def format_profile_for_prompt(profile) -> str:
    """把用户画像格式化为 Prompt 文本。"""
    if profile is None:
        return "暂无用户信息"

    parts = []
    if profile.name:
        parts.append(f"- 用户名称: {profile.name}")
    if profile.occupation:
        parts.append(f"- 职业: {profile.occupation}")
    if profile.domain_knowledge:
        parts.append(f"- 技术栈: {', '.join(profile.domain_knowledge)}")
    if profile.current_project:
        parts.append(f"- 当前项目: {profile.current_project}")
    if profile.preferences:
        pref = profile.preferences
        parts.append(f"- 回复偏好: 长度={pref.response_length}, 详细程度={pref.explanation_level}")

    return "\n".join(parts) if parts else "暂无用户信息"


prompt_with_profile = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个智能助手。请根据以下用户信息提供个性化帮助：

## 用户画像
{user_profile}

## 注意事项
- 使用用户熟悉的技术栈举例
- 根据用户的专业水平调整解释详细程度
- 考虑用户当前项目的上下文""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)


def create_personalized_chain(user_id: str, store, llm, get_session_history):
    profile = store.load(user_id)
    profile_text = format_profile_for_prompt(profile)

    def inject_profile(inputs: dict) -> dict:
        return {**inputs, "user_profile": profile_text}

    base_chain = inject_profile | prompt_with_profile | llm

    return RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
