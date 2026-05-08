"""RedisUserProfileStore — 用户画像持久化到 Redis

对应课程章节：第七章 / 5.2
"""
import json
import os
from datetime import datetime
from typing import Optional

import redis
from dotenv import load_dotenv

# from .09_user_profile_pydantic import UserProfile
class UserProfile:                       # placeholder
    pass

load_dotenv()


class RedisUserProfileStore:
    """基于 Redis 的用户画像存储服务。

    Redis Key: {key_prefix}:{user_id}    存储 JSON 字符串
    """

    def __init__(self, key_prefix: str = "user_profile"):
        self.key_prefix = key_prefix
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB", "15")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
        )

    def _get_key(self, user_id: str) -> str:
        return f"{self.key_prefix}:{user_id}"

    def save(self, profile: "UserProfile", ttl: Optional[int] = None) -> None:
        profile.updated_at = datetime.now()
        key = self._get_key(profile.user_id)
        json_data = profile.model_dump_json()
        if ttl:
            self.client.setex(key, ttl, json_data)
        else:
            self.client.set(key, json_data)

    def load(self, user_id: str) -> Optional["UserProfile"]:
        key = self._get_key(user_id)
        data = self.client.get(key)
        if data is None:
            return None
        return UserProfile(**json.loads(data))

    def get_or_create(self, user_id: str) -> "UserProfile":
        profile = self.load(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            self.save(profile)
        return profile

    def update(self, user_id: str, **kwargs) -> Optional["UserProfile"]:
        profile = self.load(user_id)
        if profile is None:
            return None
        for k, v in kwargs.items():
            if hasattr(profile, k):
                setattr(profile, k, v)
        self.save(profile)
        return profile

    def delete(self, user_id: str) -> bool:
        key = self._get_key(user_id)
        return self.client.delete(key) > 0

    def exists(self, user_id: str) -> bool:
        return self.client.exists(self._get_key(user_id)) > 0

    def list_all_users(self) -> list[str]:
        pattern = f"{self.key_prefix}:*"
        keys = self.client.keys(pattern)
        prefix_len = len(self.key_prefix) + 1
        return [k[prefix_len:] for k in keys]


if __name__ == "__main__":
    store = RedisUserProfileStore()

    profile = UserProfile(
        user_id="user_001",
        name="小明",
        occupation="Python开发工程师",
        domain_knowledge=["Python", "FastAPI"],
        current_project="电商系统",
    )
    store.save(profile)
    loaded = store.load("user_001")
    print(f"加载用户: {loaded.name}, 职业: {loaded.occupation}")

    store.update("user_001", current_project="推荐系统v2")
    print(f"更新后项目: {store.load('user_001').current_project}")

    print(f"所有用户: {store.list_all_users()}")
    print(f"user_001 存在: {store.exists('user_001')}")
