from typing import Annotated

from fastapi import APIRouter, UploadFile
from fastapi.params import Body, Depends, File, Path
from fastapi.responses import FileResponse

from microblog.api.dependencies import (
    get_current_user,
    get_media_service,
    get_tweet_service,
    get_user_service,
)
from microblog.api.schemas import (
    CreateTweetSchema,
    FollUnfollowSchema,
    TweetsResponseSchema,
    TweetSuccessSchema,
    UserResponseSchema,
    UserSchemaOut,
)
from microblog.db.models import User
from microblog.logger import get_logger
from microblog.services.media_service import MediaService
from microblog.services.tweet_service import TweetService
from microblog.services.user_service import UserService

logger = get_logger(__name__)

# Роутеры
start_router = APIRouter(tags=["Стартовый"])
users_router = APIRouter(prefix="/api/users", tags=["Пользователи"])
tweets_router = APIRouter(prefix="/api/tweets", tags=["Твиты"])
medias_router = APIRouter(prefix="/api/medias", tags=["Медиа"])

# Аннотации для ручек
CurrentUser = Annotated[User, Depends(get_current_user)]
IdUserAnnotated = Annotated[int, Path(..., description="ID Пользователя")]
ServiceUserAnnotated = Annotated[UserService, Depends(get_user_service)]
ServiceTweetAnnotated = Annotated[TweetService, Depends(get_tweet_service)]
IdTweetAnnotated = Annotated[int, Path(..., description="ID Твита")]
ServiceMediaAnnotated = Annotated[MediaService, Depends(get_media_service)]


@start_router.get("/", summary="Загрузка статики")
async def read_index():
    return FileResponse("static/index.html")


@users_router.get("/me", summary="Получить по API")
async def get_me(
    authenticated_user: CurrentUser,
) -> UserResponseSchema:
    """Ручка получения пользователя по api-key
    вызывается при запросе фронта, заглушка"""
    user_schema = UserSchemaOut.model_validate(authenticated_user, from_attributes=True)
    return UserResponseSchema(result=True, user=user_schema)


@users_router.get("/{id_user}", summary="Получить по ID")
async def get_user_by_id(
    _: CurrentUser,
    id_user: IdUserAnnotated,
    user_service: ServiceUserAnnotated,
) -> UserResponseSchema:
    """Ручка получения пользователя по ID"""

    return await user_service.get_user_profile(
        user_id=id_user,
    )


@users_router.post("/{id_user}/follow", summary="Подписаться по ID")
async def follow_user_by_id(
    current_user: CurrentUser,
    id_user: IdUserAnnotated,
    user_service: ServiceUserAnnotated,
) -> FollUnfollowSchema:
    """Ручка подписи на пользователя по ID"""

    return await user_service.follow_user(
        user_id=id_user,
        user=current_user,
    )


@users_router.delete("/{id_user}/follow", summary="Отписаться по ID")
async def unfollow_user_by_id(
    current_user: CurrentUser,
    id_user: IdUserAnnotated,
    user_service: ServiceUserAnnotated,
) -> FollUnfollowSchema:
    """Ручка отписки от пользователя по ID"""

    return await user_service.unfollow_user(
        user_id=id_user,
        user=current_user,
    )


@tweets_router.post("", summary="Опубликовать твит")
async def post_tweet(
    current_user: CurrentUser,
    tweet_service: ServiceTweetAnnotated,
    tweet_data: Annotated[str, Body(..., description="Твит")],
    tweet_media_ids: Annotated[list[int] | None, Body()] = None,
) -> CreateTweetSchema | UserResponseSchema:
    """Ручка публикации твита"""

    return await tweet_service.create_tweet(
        user=current_user, data=tweet_data, media_ids=tweet_media_ids
    )


@tweets_router.get("", summary="Получить твиты")
async def get_tweets(
    current_user: CurrentUser,
    tweet_service: ServiceTweetAnnotated,
    all_tweets: bool = True,
) -> TweetsResponseSchema | UserResponseSchema:
    """Ручка получения всех твитов на кого подписан пользователь при all_tweets=False,
    Ручка получения всех твитов при all_tweets=True"""

    return await tweet_service.get_tweets(user=current_user, all_tweets=all_tweets)


@tweets_router.delete("/{id_tweet}", summary="Удалить по ID")
async def delete_tweet(
    current_user: CurrentUser,
    tweet_service: ServiceTweetAnnotated,
    id_tweet: IdTweetAnnotated,
) -> TweetSuccessSchema:
    """Ручка для удаления твита"""
    return await tweet_service.delete_tweet(
        user=current_user,
        tweet_id=id_tweet,
    )


@tweets_router.post("/{id_tweet}/likes", summary="Лайкнуть по ID")
async def like_tweet(
    current_user: CurrentUser,
    tweet_service: ServiceTweetAnnotated,
    id_tweet: IdTweetAnnotated,
) -> TweetSuccessSchema:
    """Ручка для установки лайка, если его нет и обратное"""
    return await tweet_service.like_tweet(
        user=current_user,
        tweet_id=id_tweet,
    )


@tweets_router.delete("/{id_tweet}/likes", summary="Убрать лайк по ID")
async def unlike_tweet(
    current_user: CurrentUser,
    tweet_service: ServiceTweetAnnotated,
    id_tweet: IdTweetAnnotated,
) -> TweetSuccessSchema:
    """Ручка для убирания лайка, если его нет и обратное"""
    return await tweet_service.unlike_tweet(
        user=current_user,
        tweet_id=id_tweet,
    )


@medias_router.post("", summary="Загрузка медиа")
async def upload_media(
    current_user: CurrentUser,
    media_service: ServiceMediaAnnotated,
    file: Annotated[UploadFile, File(...)],
):
    """Ручка загрузки медиа из твита"""
    return await media_service.upload_media(user=current_user, file=file)
