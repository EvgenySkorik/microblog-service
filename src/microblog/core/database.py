from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from microblog.config import settings
from microblog.db.base import Base
from microblog.logger import get_logger

logger = get_logger(__name__)

AsyncEngine = create_async_engine(settings.POSTGRES.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=AsyncEngine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генерирует асинхронную сессию для каждого запроса."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with AsyncEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Создание таблиц в БД")


async def delete_tables():
    async with AsyncEngine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Удаление таблиц из БД")
