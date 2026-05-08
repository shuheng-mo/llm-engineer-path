"""Memory 综合实战 — Redis 短期 + Postgres 长期 + 自动抽取画像

对应课程章节：第七章 / 6 综合实战

依赖:
uv pip install psycopg2-binary
"""
"""
Memory 综合实战：具备短期 + 长期记忆的聊天机器人
- 短期记忆：Redis（对话历史）
- 长期记忆：PostgreSQL（用户画像）
"""
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, DateTime, String, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


# === 1. 模型 ===
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.3,
)
extract_llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL_NAME"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0,
)


# === 2. 数据库连接 ===
REDIS_URL = "redis://:{password}@{host}:{port}/{db}".format(
    password=os.getenv("REDIS_PASSWORD"),
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=os.getenv("REDIS_DB", "15"),
)

pg_url_object = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=int(os.getenv("PG_PORT")),
    database=os.getenv("PG_DB"),
)

engine = create_engine(pg_url_object, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# === 3. 数据模型 ===
class UserPreferences(BaseModel):
    response_length: str = Field(default="medium")
    detail_level: str = Field(default="intermediate")
    language: str = Field(default="zh-CN")


class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    occupation: Optional[str] = None
    domain_knowledge: list[str] = Field(default_factory=list)
    current_project: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExtractedInfo(BaseModel):
    name: Optional[str] = None
    occupation: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    project: Optional[str] = None
    has_new_info: bool = False


class UserProfileDB(Base):
    __tablename__ = "user_profiles"
    user_id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=True)
    occupation = Column(String(200), nullable=True)
    domain_knowledge = Column(JSON, default=list)
    current_project = Column(String(500), nullable=True)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(engine)


# === 4. PostgreSQL 长期画像存储 ===
class PostgresUserProfileStore:
    def __init__(self):
        self.SessionLocal = SessionLocal

    def save(self, profile: UserProfile) -> None:
        with self.SessionLocal() as session:
            db_profile = session.query(UserProfileDB).filter(
                UserProfileDB.user_id == profile.user_id
            ).first()
            if db_profile:
                db_profile.name = profile.name
                db_profile.occupation = profile.occupation
                db_profile.domain_knowledge = profile.domain_knowledge
                db_profile.current_project = profile.current_project
                db_profile.preferences = profile.preferences.model_dump()
            else:
                db_profile = UserProfileDB(
                    user_id=profile.user_id,
                    name=profile.name,
                    occupation=profile.occupation,
                    domain_knowledge=profile.domain_knowledge,
                    current_project=profile.current_project,
                    preferences=profile.preferences.model_dump(),
                )
                session.add(db_profile)
            session.commit()

    def load(self, user_id: str) -> Optional[UserProfile]:
        with self.SessionLocal() as session:
            db_profile = session.query(UserProfileDB).filter(
                UserProfileDB.user_id == user_id
            ).first()
            if db_profile is None:
                return None
            return UserProfile(
                user_id=db_profile.user_id,
                name=db_profile.name,
                occupation=db_profile.occupation,
                domain_knowledge=db_profile.domain_knowledge or [],
                current_project=db_profile.current_project,
                preferences=UserPreferences(**(db_profile.preferences or {})),
                created_at=db_profile.created_at,
                updated_at=db_profile.updated_at,
            )

    def get_or_create(self, user_id: str) -> UserProfile:
        profile = self.load(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            self.save(profile)
        return profile


# === 5. Redis 短期记忆管理 ===
class RedisSessionManager:
    def __init__(self, ttl: int = 3600):
        self.redis_url = REDIS_URL
        self.ttl = ttl

    def get_history(self, session_id: str) -> RedisChatMessageHistory:
        return RedisChatMessageHistory(session_id=session_id, url=self.redis_url, ttl=self.ttl)

    def clear_session(self, session_id: str) -> None:
        self.get_history(session_id).clear()


# === 6. 信息抽取 ===
class InfoExtractor:
    def __init__(self, llm):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """从用户消息中提取以下信息（仅提取明确提到的，不要推测）：
- name: 用户名字
- occupation: 职业
- skills: 技能列表
- project: 当前项目
- has_new_info: 是否包含新信息（如果消息中有任何上述信息则为 true）

输出 JSON 格式，未提到的字段为 null 或空列表。"""),
            ("human", "{message}"),
        ])
        self.chain = self.prompt | llm | JsonOutputParser()

    def extract(self, message: str) -> ExtractedInfo:
        try:
            return ExtractedInfo(**self.chain.invoke({"message": message}))
        except Exception as e:
            print(f"信息抽取失败: {e}")
            return ExtractedInfo()


# === 7. MemoryBot 主类 ===
class MemoryBot:
    def __init__(self, session_ttl: int = 3600):
        self.profile_store = PostgresUserProfileStore()
        self.session_manager = RedisSessionManager(ttl=session_ttl)
        self.extractor = InfoExtractor(extract_llm)

        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，具备记忆能力。

## 用户画像（长期记忆）
{user_profile}

## 注意事项
- 根据用户背景调整回复风格
- 使用用户熟悉的技术举例
- 保持自然的对话风格
- 记住当前对话的上下文"""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        self.chat_chain = self.chat_prompt | llm | StrOutputParser()

    def _format_profile(self, profile: UserProfile) -> str:
        parts = []
        if profile.name:
            parts.append(f"- 姓名: {profile.name}")
        if profile.occupation:
            parts.append(f"- 职业: {profile.occupation}")
        if profile.domain_knowledge:
            parts.append(f"- 技能: {', '.join(profile.domain_knowledge)}")
        if profile.current_project:
            parts.append(f"- 当前项目: {profile.current_project}")
        return "\n".join(parts) if parts else "暂无用户信息"

    def _update_profile(self, user_id: str, message: str) -> None:
        extracted = self.extractor.extract(message)
        if not extracted.has_new_info:
            return

        profile = self.profile_store.get_or_create(user_id)
        if extracted.name:
            profile.name = extracted.name
        if extracted.occupation:
            profile.occupation = extracted.occupation
        if extracted.skills:
            profile.domain_knowledge = list(set(profile.domain_knowledge + extracted.skills))
        if extracted.project:
            profile.current_project = extracted.project
        self.profile_store.save(profile)

    def chat(self, user_id: str, session_id: str, message: str) -> str:
        self._update_profile(user_id, message)

        profile = self.profile_store.get_or_create(user_id)
        profile_text = self._format_profile(profile)

        def inject_profile(inputs: dict) -> dict:
            return {**inputs, "user_profile": profile_text}

        chain_with_profile = RunnableLambda(inject_profile) | self.chat_chain
        chain_with_history = RunnableWithMessageHistory(
            chain_with_profile,
            lambda sid: self.session_manager.get_history(sid),
            input_messages_key="input",
            history_messages_key="history",
        )

        config = {"configurable": {"session_id": session_id}}
        return chain_with_history.invoke({"input": message}, config=config)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.profile_store.load(user_id)

    def clear_session(self, session_id: str) -> None:
        self.session_manager.clear_session(session_id)


def main():
    bot = MemoryBot(session_ttl=3600)
    user_id = "user_001"
    session_id = f"{user_id}:session_001"

    print("=" * 60)
    print("Memory Bot - 短期记忆(Redis) + 长期记忆(PostgreSQL)")
    print("=" * 60)

    conversations = [
        "你好，我叫小明",
        "我是一名Python后端开发工程师",
        "我正在做一个电商推荐系统，用的是FastAPI和PostgreSQL",
        "我之前说我叫什么名字？做什么工作？",
        "帮我写一段代码，实现用户登录的API",
    ]

    for msg in conversations:
        print(f"\n用户: {msg}")
        response = bot.chat(user_id, session_id, msg)
        print(f"AI: {response}")
        print("-" * 40)

    print("\n" + "=" * 60)
    print("最终用户画像（PostgreSQL）：")
    profile = bot.get_profile(user_id)
    if profile:
        print(profile.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("模拟新会话（测试长期记忆）：")
    new_session_id = f"{user_id}:session_002"
    response = bot.chat(user_id, new_session_id, "你还记得我是谁吗？我在做什么项目？")
    print(f"AI: {response}")


if __name__ == "__main__":
    main()
