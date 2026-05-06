from fastapi import APIRouter
from app.api.v1.endpoints import academic, auth, notifications, chat

api_router = APIRouter()

# Import các router con
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])