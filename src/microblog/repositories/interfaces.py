from abc import ABC, abstractmethod
from typing import List

from fastapi import UploadFile

from microblog.db.models import User, Tweet


class IUserRepository(ABC):
    """Интерфейс для работы с пользователями (бизнес-уровень)"""

    @abstractmethod
    async def get_user_by_api_key(self, api_key: str) -> User | None:
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def follow_user(self, user: User, target_user_id: int) -> bool:
        pass

    @abstractmethod
    async def unfollow_user(self, user: User, target_user_id: int) -> bool:
        pass


class ITweetRepository(ABC):
    """Интерфейс для работы с твитами (бизнес-уровень)"""

    @abstractmethod
    async def create_tweet(self, user: User, data: str, media_ids: list[int] | None = None) -> int:
        pass

    @abstractmethod
    async def get_tweets(self, user: User, all_tweets: bool) -> List[Tweet]:
        pass

    @abstractmethod
    async def delete_tweet(self, user: User, tweet_id: int) -> bool:
        pass

    @abstractmethod
    async def like_tweet(self, user: User, tweet_id: int) -> bool:
        pass

    @abstractmethod
    async def unlike_tweet(self, user: User, tweet_id: int) -> bool:
        pass


class IMediaRepository(ABC):
    """Интерфейс для работы с медиа (бизнес-уровень)"""

    @abstractmethod
    async def upload_media(self, user: User, file: UploadFile) -> int:
        pass
