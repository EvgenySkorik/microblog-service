from microblog.api.schemas import MediaResponseSchema
from microblog.db.models import User
from microblog.logger import get_logger
from microblog.repositories.interfaces import IMediaRepository

logger = get_logger(__name__)


class MediaService:
    def __init__(self, media_repository: IMediaRepository):
        self._media_repo = media_repository

    async def upload_media(self, user: User, file) -> MediaResponseSchema:
        """Загрузка файлов из твита"""
        media_id = await self._media_repo.upload_media(user=user, file=file)
        logger.debug("Пользователь %s подгрузил файл %s", user.id, media_id)
        if not media_id:
            return MediaResponseSchema(result=False, media_id=None)
        return MediaResponseSchema(result=True, media_id=media_id)
