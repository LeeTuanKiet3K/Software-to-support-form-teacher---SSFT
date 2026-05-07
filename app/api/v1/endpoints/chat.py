from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.Middleware import Middleware
from app.features.chat.ContextManager import ContextManager

router = APIRouter()


def get_chat_service() -> Middleware:
    """Dependency cung cấp Middleware cho luồng chat AI."""
    return Middleware()


def get_context_service() -> ContextManager:
    """Dependency cung cấp ContextManager cho lịch sử hội thoại."""
    return ContextManager()


class ChatMessageRequest(BaseModel):
    chat_id: str = Field(..., min_length=1, description="ID phiên chat")
    student_message: str = Field(..., min_length=1, description="Nội dung người dùng gửi")


class ChatMessageResponse(BaseModel):
    chat_id: str
    answer: str


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    chat_id: str
    messages: List[ChatHistoryItem] = Field(default_factory=list)


@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: str,
    context_service: ContextManager = Depends(get_context_service),
):
    """Lấy lịch sử hội thoại gần nhất qua ContextManager."""
    history = context_service.getChatContext(chat_id=chat_id, limit=20)
    messages = [ChatHistoryItem(role=item["role"], content=item["content"]) for item in history]
    return ChatHistoryResponse(chat_id=chat_id, messages=messages)


@router.post("/message", response_model=ChatMessageResponse, status_code=201)
async def send_chat_message(
    payload: ChatMessageRequest,
    chat_service: Middleware = Depends(get_chat_service),
):
    """Gửi tin nhắn vào luồng AI qua Middleware."""
    answer = chat_service.coordinateFlow(
        studentMessage=payload.student_message,
        chatId=payload.chat_id,
    )
    return ChatMessageResponse(chat_id=payload.chat_id, answer=answer)
