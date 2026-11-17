from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend pusat kendali AI workforce Nafeka.",
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status": "online",
        "version": settings.app_version,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "nafeka-ai-office-api",
        "environment": settings.app_env,
    }
