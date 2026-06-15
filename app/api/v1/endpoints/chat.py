from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_middleware, get_orchestrator, get_aggregator, get_issue_service
from app.core.Middleware import Middleware
from app.features.chat.ChatOrchestrator import ChatOrchestrator
from app.features.chat.ContextManager import ContextManager
from app.features.chat.ResponseAggregator import ResponseAggregator
from app.features.chat.PromptTemplates import SYSTEM_PROMPT_FOR_ADVISOR
from app.services.IssueService import IssueService
from app.core.Config import AppConfig
from groq import Groq

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
    class_id: str = Field("", description="Lớp mà GVCN phụ trách")

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
async def advisor_chat(
    payload: AdvisorChatRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    """Trợ lý AI phân tích dữ liệu cho Giáo viên (Dashboard)"""
    print(f"[chat/advisor] GV ra lệnh: {payload.message} - Lớp: {payload.class_id}")
    
    # 1. Fetch real class issues
    try:
        raw_issues = issue_service.getAllIssues(advisorClassId=payload.class_id)
        # Lọc các vấn đề đang mở hoặc đang xử lý
        active_issues = [i for i in raw_issues if i.get("status") in ("OPEN", "IN_PROGRESS", "PENDING_ADVISOR")]
        
        # Build context string
        if not active_issues:
            class_context = "Hiện tại lớp không có vấn đề nào cần xử lý."
        else:
            class_context = f"Lớp hiện có {len(active_issues)} vấn đề cần xử lý:\n"
            for issue in active_issues:
                content = issue.get("content") or issue.get("student_message_preview") or "Không có nội dung"
                priority = issue.get("priority", "N/A")
                student_id = issue.get("student_id", "N/A")
                class_context += f"- Sinh viên {student_id} (Ưu tiên: {priority}): {content}\n"
    except Exception as e:
        print(f"[chat/advisor] Lỗi lấy dữ liệu lớp: {e}")
        class_context = "Không thể lấy dữ liệu lớp học lúc này do lỗi hệ thống."

    # 2. Call Groq
    apiKey = AppConfig.GROQ_API_KEY
    if not apiKey:
        return {
            "content": "Hệ thống AI hiện đang bảo trì (Thiếu API Key). Thầy/Cô vui lòng thử lại sau.",
            "actions": [],
            "dataTable": None
        }

    try:
        groqClient = Groq(api_key=apiKey)
        system_prompt = SYSTEM_PROMPT_FOR_ADVISOR.format(
            class_context=class_context,
            user_message=payload.message
        )
        
        completion = groqClient.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.message},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        ai_response = completion.choices[0].message.content
        
        # 3. Build response
        response = {
            "content": ai_response,
            "actions": ["Tạo thông báo lớp", "Lọc SV rớt môn"],
            "dataTable": None
        }
        
        # Giữ lại logic mock cho bảng dữ liệu rớt môn nếu có từ khóa
        if "lọc" in payload.message.lower() or "rớt" in payload.message.lower() or "cảnh báo" in payload.message.lower():
            response["dataTable"] = {
                "headers": ["MSSV", "Họ Tên", "GPA", "Tình trạng"],
                "rows": [
                    ["24120101", "Trần Quang Tuấn", "1.8", "Nguy cơ cao"],
                    ["24120105", "Hoàng Thị Yến", "2.0", "Cần theo dõi"]
                ]
            }
            response["actions"] = ["Xuất file Excel", "Gửi email nhắc nhở"]

        return response
    except Exception as e:
        print(f"[chat/advisor] Lỗi gọi Groq: {e}")
        return {
            "content": "Trợ lý AI đang gặp sự cố kết nối. Thầy/Cô vui lòng thử lại sau.",
            "actions": [],
            "dataTable": None
        }


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