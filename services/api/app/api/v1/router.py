from fastapi import APIRouter

from app.api.v1.endpoints import audit, auth, resources

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(resources.router)
api_router.include_router(audit.router)
