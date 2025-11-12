from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator

from microblog.config import settings
from microblog.logger import get_logger

logger = get_logger()


class UserAuthorSchema(BaseModel):
    id: int
    name: str


class UserSchemaOut(UserAuthorSchema):
    followers: list[UserAuthorSchema] = []
    following: list[UserAuthorSchema] = []


class UserResponseSchema(BaseModel):
    result: bool
    user: UserSchemaOut | None


class FollUnfollowSchema(BaseModel):
    result: bool
    message: str


class TweetSuccessSchema(BaseModel):
    result: bool
    message: str


class UserLikeSchema(BaseModel):
    user_id: int = Field(..., alias="id", serialization_alias="user_id")
    name: str


class CreateTweetSchema(BaseModel):
    result: bool
    tweet_id: int | None


class TweetShemaOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserAuthorSchema
    attachments: list[str] = []
    likes: list[UserLikeSchema] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stamp(self) -> str:
        """Принудительная конвертация времени в UTC для фронта"""
        if self.created_at.tzinfo is None:
            utc_time = self.created_at.replace(tzinfo=UTC)
        else:
            utc_time = self.created_at.astimezone(UTC)

        return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    @field_validator("attachments", mode="before")
    @classmethod
    def transform_attachments(cls, value: Any) -> Any:
        """Автоматически преобразует объекты Media в пути"""
        if not value:
            return []

            # Если это уже строки - возвращаем как есть
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return [f"{settings.MEDIA.MEDIA_URL}{item}?size=small" for item in value]

            # Если это объекты Media - извлекаем пути
        if isinstance(value, list) and hasattr(value[0], "path"):
            return [
                f"{settings.MEDIA.MEDIA_URL}{media.path}?size=small" for media in value
            ]

        return value


class TweetsResponseSchema(BaseModel):
    result: bool
    tweets: list[TweetShemaOut] | None


class MediaResponseSchema(BaseModel):
    result: bool
    media_id: int | None
