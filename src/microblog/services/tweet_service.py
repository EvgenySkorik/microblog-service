from fastapi import HTTPException, status

from microblog.api.schemas import (
    CreateTweetSchema,
    TweetsResponseSchema,
    TweetSuccessSchema,
    UserResponseSchema,
)
from microblog.db.models import User
from microblog.logger import get_logger
from microblog.repositories.interfaces import ITweetRepository

logger = get_logger(__name__)


class TweetService:
    def __init__(self, tweet_repository: ITweetRepository) -> None:
        self._tweet_repo = tweet_repository

    async def create_tweet(
        self, user: User, data: str, media_ids=None
    ) -> UserResponseSchema | CreateTweetSchema:
        """Создание твита"""
        if not user:
            return UserResponseSchema(result=False, user=None)

        tweet_id = await self._tweet_repo.create_tweet(
            user=user, data=data, media_ids=media_ids
        )
        if not tweet_id:
            return CreateTweetSchema(result=False, tweet_id=None)
        logger.info("Пользователь %s опубликовал твит %s", user.id, tweet_id)

        return CreateTweetSchema(result=True, tweet_id=tweet_id)

    async def get_tweets(self, user: User, all_tweets: bool) -> TweetsResponseSchema:
        """Получения списка твитов"""
        tweets = await self._tweet_repo.get_tweets(user=user, all_tweets=all_tweets)
        if not tweets:
            return TweetsResponseSchema(result=False, tweets=None)
        logger.info("Пользователь %s получил список твитов", user.id)

        return TweetsResponseSchema(result=True, tweets=tweets)

    async def delete_tweet(self, user: User, tweet_id: int) -> TweetSuccessSchema:
        """Удаление твита по ID"""
        success = await self._tweet_repo.delete_tweet(user=user, tweet_id=tweet_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Твит не найден или нет прав для удаления",
            )
        logger.info("Пользователь %s удалил твит %s", user.id, tweet_id)

        return TweetSuccessSchema(
            result=success, message="Ok delete" if success else "Oops"
        )

    async def like_tweet(self, user: User, tweet_id: int) -> TweetSuccessSchema:
        """Отметить лайка на твите по ID"""
        success = await self._tweet_repo.like_tweet(user=user, tweet_id=tweet_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ошибка снятия отметки"
            )
        logger.info("Пользователь %s лайкнул твит %s", user.id, tweet_id)

        return TweetSuccessSchema(
            result=success, message="Ok like" if success else "Oops"
        )

    async def unlike_tweet(self, user: User, tweet_id: int) -> TweetSuccessSchema:
        """Снять отметку лайка с твита по ID"""
        success = await self._tweet_repo.unlike_tweet(user=user, tweet_id=tweet_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ошибка снятия отметки"
            )
        logger.info("Пользователь %s снял лайк с твита %s", user.id, tweet_id)

        return TweetSuccessSchema(
            result=success, message="Ok unlike" if success else "Oops"
        )
