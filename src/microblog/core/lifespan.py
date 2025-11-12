import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from microblog.config import settings
from microblog.core.database import (
    create_tables,
)
from microblog.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Запуск FastAPI")
    await create_tables()
    logger.info("Подключение, создание таблиц в БД")

    os.makedirs(settings.MEDIA.upload_dir, exist_ok=True)
    logger.info(f"Создание папки для медиа - {settings.MEDIA.upload_dir}, если её нет")
    yield
    # await AsyncEngine.dispose()
    # await delete_tables()
    print("Завершение FastAPI")
