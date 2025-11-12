import os
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Класс с настройками PostgreSQL"""

    SERVER: str = "db"
    USER: str = "postgres"
    PASSWORD: str = "password"
    DB: str = "microblog_dev"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.SERVER}/{self.DB}"
        )


class UvicornSettings(BaseSettings):
    """Класс с настройками сервера UVICORN"""

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 1
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "dev"

    @property
    def uvicorn_reload(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def uvicorn_workers(self) -> int:
        return 1 if self.ENVIRONMENT == "dev" else os.cpu_count() or 1


class MediaSettings(BaseSettings):
    """Настройки для медиа"""

    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent
    UPLOAD_FOLDER: str = "static/uploads"
    MAX_FILE_SIZE: int = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif,bmp,webp"
    MEDIA_URL: str = "/uploads/"

    @property
    def upload_dir(self) -> Path:
        """Абсолютный путь к папке загрузок"""
        return self.BASE_DIR / self.UPLOAD_FOLDER

    @property
    def allowed_extensions(self) -> list:
        return self.ALLOWED_EXTENSIONS.split(",")


class AppSettings(BaseSettings):
    """Класс с общими настройками"""

    PROJECT_NAME: str = "Microblog Service"
    ENVIRONMENT: str = "dev"
    DESCRIPTION: str = "_Microblog API_"
    VERSION: str = "1.0.0"
    CONTACT_NAME: str = "Скорик Евгений"
    CONTACT_EMAIL: str = "3653444@bk.ru"

    POSTGRES: DatabaseSettings = DatabaseSettings()
    UVICORN: UvicornSettings = UvicornSettings()
    MEDIA: MediaSettings = MediaSettings()

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_nested_delimiter="__",
        case_sensitive=True,
    )


settings: AppSettings = AppSettings()
