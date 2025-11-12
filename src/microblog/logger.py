import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE_NAME = "microblog.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
(LOG_DIR / "__init__.py").touch(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_DIR / LOG_FILE_NAME,
    filemode="a",
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    encoding="utf-8",
    force=True,
)


def get_logger(name=None):
    """Возвращает настроенный логгер"""
    return logging.getLogger(name or __name__)
