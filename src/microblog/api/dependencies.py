from __future__ import annotations

from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from microblog.core.database import get_db
from microblog.db.models import User
from microblog.repositories.interfaces import IMediaRepository, ITweetRepository
from microblog.repositories.repository import (
    MediaRepository,
    TweetRepository,
    UserRepository,
)
from microblog.services.media_service import MediaService
from microblog.services.tweet_service import TweetService
from microblog.services.user_service import UserService


async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


async def get_tweet_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ITweetRepository:
    return TweetRepository(db)


async def get_tweet_service(
    tweet_repo: Annotated[ITweetRepository, Depends(get_tweet_repository)],
) -> TweetService:
    return TweetService(tweet_repo)


async def get_media_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IMediaRepository:
    return MediaRepository(db)


async def get_media_service(
    media_repo: Annotated[IMediaRepository, Depends(get_media_repository)],
) -> MediaService:
    return MediaService(media_repo)


async def get_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    api_key: Annotated[str, Header(..., description="Ключ текущего пользователя")],
) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ключа пользователя API-Key не существует",
        )
    user = await user_service._user_repo.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не верный ключ API-Key для данного пользователя",
        )

    return user  # type: ignore
