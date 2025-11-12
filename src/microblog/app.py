from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from microblog.api.routes import (
    medias_router,
    start_router,
    tweets_router,
    users_router,
)
from microblog.config import settings
from microblog.core.lifespan import lifespan
from microblog.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        contact={
            "name": settings.CONTACT_NAME,
            "email": settings.CONTACT_EMAIL,
        },
        lifespan=lifespan,
    )
    logger.debug(f"Создание экземпляра приложения: {settings.PROJECT_NAME}")

    routers = [
        ("start_router", start_router),
        ("users_router", users_router),
        ("tweets_router", tweets_router),
        ("medias_router", medias_router),
    ]

    for name, router in routers:
        app.include_router(router)
        logger.debug(f"Подключен роутер: {name}")

    app.mount("/", StaticFiles(directory="static"))
    logger.debug("Подключены статические файлы")

    logger.info(f"Приложение {settings.PROJECT_NAME} успешно создано")

    return app
