from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_middleware, get_orchestrator, get_aggregator
from app.core.Middleware import Middleware
from app.features.chat.ChatOrchestrator import ChatOrchestrator
from app.features.chat.ContextManager import ContextManager
from app.features.chat.ResponseAggregator import ResponseAggregator

router = APIRouter()


# ---------------------------------------------------------
# Dependency Injection Helpers
# ---------------------------------------------------------

def get_context_service() -> ContextManager:
    """Dependency cung cấp ContextManager để truy vấn lịch sử hội thoại."""
    return ContextManager()


# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------

class ChatMessageRequest(BaseModel):
    chat_id: str = Field(..., min_length=1, description="ID phiên chat (thường là UID người dùng)")
    student_id: str = Field(..., min_length=1, description="UID sinh viên gửi tin nhắn")
    student_message: str = Field(..., min_length=1, description="Nội dung tin nhắn người dùng gửi")


class ChatMessageResponse(BaseModel):
    chat_id: str
    answer: str
    quick_actions: List[str] = Field(default_factory=list, description="Danh sách thao tác nhanh AI đề xuất")
    priority_level: Optional[str] = Field(None, description="Mức ưu tiên phát hiện (P0/P1/P2/INVALID)")
    category: Optional[str] = Field(None, description="Danh mục vấn đề AI phân loại")
    is_fallback: bool = Field(False, description="True nếu không khớp từ khóa và dùng Gemini fallback")


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    chat_id: str
    messages: List[ChatHistoryItem] = Field(default_factory=list)


class ChatSummaryResponse(BaseModel):
    chat_id: str
    secret_summary: str = Field(description="Tóm tắt nội dung chat dành riêng cho GVCN (ADVISOR_ONLY)")
    privacy_tag: str = Field(default="ADVISOR_ONLY")


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@router.post("/message", response_model=ChatMessageResponse, status_code=201)
async def send_chat_message(
    payload: ChatMessageRequest,
    middleware: Middleware = Depends(get_middleware),
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """
    Gửi tin nhắn vào luồng AI.

    Luồng xử lý:
      1. ChatOrchestrator phân loại mức độ ưu tiên qua PriorityLogic
      2. Truy xuất ngữ cảnh RAG từ KnowledgeBase
      3. Gemini sinh câu trả lời theo tier prompt (P0/P1/P2)
      4. Ghi Issue tự động nếu phát hiện tâm lý hoặc khiếu nại
    """
    try:
        result = orchestrator.processTurn(
            middleware=middleware,
            studentMessage=payload.student_message,
            chatId=payload.chat_id,
            studentId=payload.student_id,
        )
    except Exception as e:
        print(f"[chat/message] Lỗi xử lý luồng AI (AI pipeline error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Hệ thống AI đang tạm thời gián đoạn. Vui lòng thử lại sau."
        )

    return ChatMessageResponse(
        chat_id=payload.chat_id,
        answer=result.get("answer", ""),
        quick_actions=result.get("quick_actions", []),
        priority_level=result.get("priority_level"),
        category=result.get("category"),
        is_fallback=result.get("is_fallback", False),
    )


@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: str,
    context_service: ContextManager = Depends(get_context_service),
):
    """
    Lấy lịch sử hội thoại gần nhất của một phiên chat.
    Giới hạn 20 tin nhắn gần nhất để tối ưu hiệu năng.
    """
    history = context_service.getChatContext(chat_id=chat_id, limit=20)
    messages = [
        ChatHistoryItem(role=item["role"], content=item["content"])
        for item in history
    ]
    return ChatHistoryResponse(chat_id=chat_id, messages=messages)


@router.get("/summary/{chat_id}", response_model=ChatSummaryResponse)
async def get_chat_summary_for_advisor(
    chat_id: str,
    aggregator: ResponseAggregator = Depends(get_aggregator),
):
    """
    Lấy bản tóm tắt nội dung chat dành riêng cho GVCN (ADVISOR_ONLY).
    Dữ liệu này không được phép hiển thị ở phía sinh viên.

    Tương đương renderAdvisorDashboard → aggregator.createSummaryForAdvisor() trong main.py cũ.
    """
    try:
        summary_data = aggregator.createSummaryForAdvisor(chat_id)
    except Exception as e:
        print(f"[chat/summary] Lỗi tạo tóm tắt GVCN (summary error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể tạo tóm tắt phiên chat. Vui lòng thử lại."
        )

    return ChatSummaryResponse(
        chat_id=summary_data.get("chat_id", chat_id),
        secret_summary=summary_data.get("secret_summary", ""),
        privacy_tag=summary_data.get("privacy_tag", "ADVISOR_ONLY"),
    )
