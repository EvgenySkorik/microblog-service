import uvicorn

from microblog.app import create_app
from microblog.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "microblog.main:app",
        host=settings.UVICORN.HOST,
        port=settings.UVICORN.PORT,
        reload=settings.UVICORN.RELOAD,
        workers=settings.UVICORN.WORKERS,
        log_level=settings.UVICORN.LOG_LEVEL.lower(),
    )
