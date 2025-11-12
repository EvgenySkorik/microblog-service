from datetime import datetime
from typing import TypeVar

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from microblog.api.schemas import TweetShemaOut
from microblog.config import settings
from microblog.db.models import Media, Tweet, User
from microblog.logger import get_logger
from microblog.repositories.interfaces import (
    IMediaRepository,
    ITweetRepository,
    IUserRepository,
)

T = TypeVar("T")

logger = get_logger(__name__)


class BaseRepository[T]:
    """Базовый абстрактный класс для взаимодействия модели и БД"""

    def __init__(self, session: AsyncSession, model):
        self.session = session
        self.model = model

    async def get_by_id(self, user_id: int) -> T | None:
        """Получение модели по ID"""
        result = await self.session.execute(select(self.model).filter_by(id=user_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> T:
        """Удаление модели"""
        instance: T = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance_id: int) -> bool:
        """Удаление модели по ID"""
        instance = await self.get_by_id(instance_id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True


class UserRepository(BaseRepository[User], IUserRepository):
    """Репозиторий взаимодействия Пользователя с БД"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_user_by_api_key(self, api_key) -> User | None:
        """Получение из БД информации о валидности ключа доступа пользователя"""
        if not api_key:
            return None

        result = await self.session.execute(
            select(User)
            .options(selectinload(User.followers), selectinload(User.following))
            .where(User.api_key == api_key)
        )
        logger.debug("Запрос пользователя по ключю к БД")

        return result.scalar_one_or_none()

    async def get_user_profile(self, user_id: int) -> User | None:
        """Получение из БД подробной информации по пользователю"""
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.followers),
                selectinload(User.following),
                selectinload(User.tweets),
                selectinload(User.liked_tweets),
            )
            .where(User.id == user_id)
        )
        logger.debug("Запрос пользователя по ID к БД")

        return result.scalar_one_or_none()

    async def follow_user(self, user: User, target_user_id: int) -> bool:
        """Получение из БД пользователя, подписка"""
        await self.session.refresh(user, ["following", "followers"])
        target_user = await self.get_by_id(target_user_id)
        if not target_user or user.id == target_user.id:
            return False

        if target_user in user.following:
            return False

        user.following.append(target_user)

        await self.session.commit()
        logger.debug(f"{user.name} подписался на {target_user.name}")

        return True

    async def unfollow_user(self, user: User, target_user_id: int) -> bool:
        """Получение из БД пользователя, отписка"""
        await self.session.refresh(user, ["following", "followers"])
        target_user = await self.get_by_id(target_user_id)
        if not target_user or user.id == target_user.id:
            return False
        if target_user in user.followers:
            return False
        user.following.remove(target_user)

        await self.session.commit()
        logger.debug(f"{user.name} отписался от {target_user.name}")

        return True


class TweetRepository(BaseRepository[Tweet], ITweetRepository):
    """Репозиторий взаимодействия Твита с БД"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Tweet)
        self.user_repo = UserRepository(session)

    async def create_tweet(self, user: User, data: str, media_ids=None):
        """Создание твита в БД"""
        tweet: Tweet = await self.create(
            content=data, created_at=datetime.now(), author_id=user.id
        )

        self.session.add(tweet)
        await self.session.flush()

        if media_ids:
            for media_id in media_ids:
                media = await self.session.get(Media, media_id)
                if media:
                    media.tweet_id = tweet.id

        await self.session.commit()
        logger.debug(f"{user.name} опубликовал твит: {tweet.id}")

        return tweet.id

    async def get_tweets(self, user: User, all_tweets: bool):
        """Получение серриализованного списка твитов из БД,
        его сортировка по подписчикам при all_tweets=False"""
        query = select(Tweet).options(
            selectinload(Tweet.author),
            selectinload(Tweet.attachments),
            selectinload(Tweet.likes),
        )

        if not all_tweets:
            following_ids = [followed.id for followed in user.following]
            if not following_ids:
                tweets_shema: list = []
                return tweets_shema

            query = query.where(Tweet.author_id.in_(following_ids))

        tweets = (
            (await self.session.execute(query.order_by(Tweet.created_at.desc())))
            .scalars()
            .all()
        )

        tweets_shema = [
            TweetShemaOut.model_validate(tweet, from_attributes=True)
            for tweet in tweets
        ]
        tweets_shema.sort(key=lambda t: len(t.likes), reverse=True)
        logger.debug("Запрос пользователя твитов к БД")

        return tweets_shema

    async def delete_tweet(self, user: User, tweet_id: int):
        """Удаление твита из БД"""
        tweet = await self.get_by_id(tweet_id)
        if not tweet:
            return False
        logger.debug(f"Запрос {user.id} удаления твита {tweet_id} к БД")

        return await self.delete(tweet_id) if user.id == tweet.author_id else False

    async def like_tweet(self, user: User, tweet_id: int):
        """Добавление записи о лайке в БД"""
        await self.session.refresh(user, ["liked_tweets"])
        tweet = await self.get_by_id(tweet_id)

        if not tweet:
            return False

        if tweet in user.liked_tweets:
            return False

        user.liked_tweets.append(tweet)

        await self.session.commit()
        logger.debug("Запрос доб-я лайка к БД")

        return True

    async def unlike_tweet(self, user: User, tweet_id: int):
        """Удаление записи по лайку из БД"""
        await self.session.refresh(user, ["liked_tweets"])
        tweet = await self.get_by_id(tweet_id)

        if tweet not in user.liked_tweets:
            return False

        user.liked_tweets.remove(tweet)

        await self.session.commit()
        logger.debug("Запрос удал-я лайка к БД")

        return True


class MediaRepository(BaseRepository[Media], IMediaRepository):
    """Репозиторий взаимодействия Медиа с БД"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Media)
        self.user_repo = UserRepository(session)

    async def upload_media(self, user: User, file):
        """Добавление медиа в БД"""

        unique_filename = await self._validate_and_save_file(file, user.id)

        media = Media(path=unique_filename, user_id=user.id, tweet_id=None)

        self.session.add(media)
        await self.session.commit()
        logger.debug("Запрос доб-я медиа к БД")

        return media.id

    async def _validate_and_save_file(self, file, user_id):
        """Валидация файла, генерация имени, запись"""
        if not (
            "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower()
            in settings.MEDIA.ALLOWED_EXTENSIONS
        ):
            return False

        unique_filename = (
            f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        )
        file_path = settings.MEDIA.upload_dir / unique_filename

        contents = await file.read()

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)
        logger.debug("Валидация медиа успешна")

        return unique_filename
