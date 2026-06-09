from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_middleware, get_orchestrator, get_aggregator
from app.core.Middleware import Middleware
from app.features.chat.ChatOrchestrator import ChatOrchestrator
from app.features.chat.ContextManager import ContextManager
from app.features.chat.ResponseAggregator import ResponseAggregator

router = APIRouter()

def get_context_service() -> ContextManager:
    return ContextManager()

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class StudentChatRequest(BaseModel):
    # Lấy thông tin từ Frontend gửi lên
    message: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)

class AdvisorChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class ChatMessageResponse(BaseModel):
    chat_id: str
    answer: str
    quick_actions: List[str] = Field(default_factory=list)
    priority_level: Optional[str] = None
    category: Optional[str] = None
    is_fallback: bool = False
    image_urls: List[str] = Field(default_factory=list)

# Schema cho History & Summary giữ nguyên
class ChatHistoryItem(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    chat_id: str
    messages: List[ChatHistoryItem] = Field(default_factory=list)

class ChatSummaryResponse(BaseModel):
    chat_id: str
    secret_summary: str
    privacy_tag: str = "ADVISOR_ONLY"


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@router.post("/student", response_model=ChatMessageResponse, status_code=201)
async def student_chat(
    payload: StudentChatRequest,
    middleware: Middleware = Depends(get_middleware),
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
):
    """Luồng AI cho sinh viên hỏi đáp, chia sẻ tâm lý"""
    chat_id = f"chat_{payload.student_id}" # Tự động tạo chat_id từ student_id
    
    try:
        result = orchestrator.processTurn(
            middleware=middleware,
            studentMessage=payload.message,
            chatId=chat_id,
            studentId=payload.student_id,
        )
    except Exception as e:
        print(f"[chat/student] Lỗi AI: {e}")
        # Dùng mock data dự phòng nếu backend AI chưa nối đủ API Key
        result = {
            "answer": "Hệ thống AI đang tạm thời gián đoạn. Vui lòng liên hệ trực tiếp với GVCN nhé.",
            "quick_actions": ["Gọi GVCN"],
            "priority_level": "INVALID",
            "category": "khac"
        }

    return ChatMessageResponse(
        chat_id=chat_id,
        answer=result.get("answer", "Xin lỗi, AI chưa thể trả lời."),
        quick_actions=result.get("quick_actions", []),
        priority_level=result.get("priority_level"),
        category=result.get("category"),
        is_fallback=result.get("is_fallback", False),
        image_urls=result.get("image_urls", []),
    )

@router.post("/advisor", status_code=201)
async def advisor_chat(payload: AdvisorChatRequest):
    """Trợ lý AI phân tích dữ liệu cho Giáo viên (Dashboard)"""
    print(f"[chat/advisor] GV ra lệnh: {payload.message}")
    
    # Mock data phản hồi
    response = {
        "content": "Hệ thống đã nhận lệnh của cô. Đây là báo cáo sơ bộ:",
        "actions": ["Tạo thông báo lớp", "Lọc SV rớt môn"],
        "dataTable": None
    }
    
    if "lọc" in payload.message.lower() or "rớt" in payload.message.lower() or "cảnh báo" in payload.message.lower():
        response["dataTable"] = {
            "headers": ["MSSV", "Họ Tên", "GPA", "Tình trạng"],
            "rows": [
                ["24120101", "Trần Quang Tuấn", "1.8", "Nguy cơ cao"],
                ["24120105", "Hoàng Thị Yến", "2.0", "Cần theo dõi"]
            ]
        }
        response["content"] = "Dạ, đây là danh sách sinh viên nằm trong diện cảnh báo học vụ dựa trên đợt điểm mới nhất:"
        response["actions"] = ["Xuất file Excel", "Gửi email nhắc nhở"]

    return response


@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: str,
    context_service: ContextManager = Depends(get_context_service),
):
    history = context_service.getChatContext(chat_id=chat_id, limit=20)
    messages = [ChatHistoryItem(role=item["role"], content=item["content"]) for item in history]
    return ChatHistoryResponse(chat_id=chat_id, messages=messages)

@router.get("/summary/{chat_id}", response_model=ChatSummaryResponse)
async def get_chat_summary_for_advisor(
    chat_id: str,
    aggregator: ResponseAggregator = Depends(get_aggregator),
):
    try:
        summary_data = aggregator.createSummaryForAdvisor(chat_id)
    except Exception as e:
        print(f"[chat/summary] Lỗi tạo tóm tắt: {e}")
        raise HTTPException(status_code=500, detail="Không thể tạo tóm tắt.")

    return ChatSummaryResponse(
        chat_id=summary_data.get("chat_id", chat_id),
        secret_summary=summary_data.get("secret_summary", ""),
        privacy_tag=summary_data.get("privacy_tag", "ADVISOR_ONLY"),
    )