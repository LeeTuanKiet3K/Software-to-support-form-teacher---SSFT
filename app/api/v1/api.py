from fastapi import APIRouter
from app.api.v1.endpoints import academic, auth, notifications, chat, issues, calendar

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
api_router.include_router(issues.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])