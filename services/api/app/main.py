from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend pusat kendali AI workforce Nafeka.",
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "status": "online",
        "version": settings.app_version,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "nafeka-ai-office-api",
        "environment": settings.app_env,
    }
