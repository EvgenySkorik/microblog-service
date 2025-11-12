from microblog.api.schemas import FollUnfollowSchema, UserResponseSchema, UserSchemaOut
from microblog.db.models import User
from microblog.logger import get_logger
from microblog.repositories.interfaces import IUserRepository

logger = get_logger(__name__)


class UserService:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository

    async def get_user_profile(self, user_id: int) -> UserResponseSchema:
        """Получение профиля пользователя"""
        logger.info("Запрос профиля пользователя %s", user_id)
        user = await self._user_repo.get_user_profile(user_id=user_id)
        if not user:
            return UserResponseSchema(result=False, user=None)

        user_schema = UserSchemaOut.model_validate(user, from_attributes=True)

        return UserResponseSchema(result=True, user=user_schema)

    async def follow_user(self, user_id: int, user: User) -> FollUnfollowSchema:
        """Подписка на пользователя"""
        logger.info("Пользователь %s подписывается на %s", user.id, user_id)
        success = await self._user_repo.follow_user(user, user_id)
        return FollUnfollowSchema(
            result=success,
            message="Успешно оформлена" if success else "Ошибка повторного подписания",
        )

    async def unfollow_user(self, user_id: int, user: User) -> FollUnfollowSchema:
        """Отписка от пользователя"""
        logger.info("Пользователь %s отписывается от %s", user.id, user_id)
        success = await self._user_repo.unfollow_user(user, user_id)
        return FollUnfollowSchema(
            result=success,
            message="Успешно удалена" if success else "Ошибка повторного удаления",
        )
