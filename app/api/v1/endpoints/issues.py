from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.api.deps import get_issue_service
from app.services.IssueService import IssueService

router = APIRouter()


# ---------------------------------------------------------
# Pydantic Schemas
# -------------------------------------from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.api.deps import get_issue_service
from app.services.IssueService import IssueService

router = APIRouter()




# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED", "PENDING_ADVISOR"}
VALID_PRIORITIES = {"URGENT", "HIGH", "MEDIUM", "LOW"}

@router.get("/summary")
async def get_dashboard_summary(
    class_id: str = "",
    issue_service: IssueService = Depends(get_issue_service)
):
    """Trả về dữ liệu KPI tổng quan cho Dashboard GVCN"""
    
    # Kéo danh sách issue từ DB
    try:
        raw_issues = issue_service.getPendingIssues(advisorClassId=class_id)
    except Exception:
        raw_issues = []

    # Mock Data cho thống kê KPI
    stats = {
        "urgent": sum(1 for i in raw_issues if i.get("priority") == "URGENT"),
        "pending": len(raw_issues),
        "resolved": 12, # Demo số đã giải quyết trong tháng
        "totalStudents": 45
    }
    
    # Format danh sách để Frontend render bảng
    formatted_issues = []
    for issue in raw_issues:
        formatted_issues.append({
            "id": issue.get("issue_id", ""),
            "issue_id": issue.get("issue_id", ""),
            "student_id": issue.get("student_id", "Ẩn danh"),
            "chat_id": issue.get("chat_id"),
            "intent": issue.get("intent"),
            "sentiment": issue.get("sentiment"),
            "priority": issue.get("priority", "LOW"),
            "status": issue.get("status", "OPEN"),
            "is_advisor_viewed": issue.get("is_advisor_viewed", False),
            "unread_by_advisor": issue.get("unread_by_advisor", 0),
            "unread_by_student": issue.get("unread_by_student", 0),
            "created_at": str(issue.get("created_at", "")),
            "updated_at": str(issue.get("updated_at", "")) if issue.get("updated_at") else None,
            "title": issue.get("title"),
            "category": issue.get("category"),
            "content": issue.get("content")
        })

    return {
        "stats": stats,
        "issues": formatted_issues
    }



class IssueResponse(BaseModel):
    """Schema một phiếu vấn đề trả về từ Firestore."""
    issue_id: str
    student_id: str
    chat_id: Optional[str] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    priority: str
    status: str
    is_advisor_viewed: bool = False
    unread_by_advisor: int = 0
    unread_by_student: int = 0
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
    # Trường bổ sung nếu SV nộp qua form
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None


class PendingIssuesResponse(BaseModel):
    """Danh sách vấn đề đang chờ xử lý, đã sắp xếp theo priority."""
    total: int
    issues: List[IssueResponse]


class UpdateIssueStatusRequest(BaseModel):
    new_status: str = Field(
        ...,
        description="Trạng thái mới (OPEN | IN_PROGRESS | RESOLVED | PENDING_ADVISOR)"
    )


class UpdateIssueStatusResponse(BaseModel):
    success: bool
    issue_id: str
    new_status: str
    message: str


class CreateIssueFromFormRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="UID sinh viên nộp")
    title: str = Field(..., min_length=3, max_length=200, description="Tiêu đề vấn đề")
    content: str = Field(..., min_length=10, description="Nội dung chi tiết vấn đề")


class CreateIssueFromFormResponse(BaseModel):
    success: bool
    issue_id: Optional[str] = None
    message: str


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED", "PENDING_ADVISOR"}
VALID_PRIORITIES = {"URGENT", "HIGH", "MEDIUM", "LOW"}


@router.get("/pending", response_model=PendingIssuesResponse)
async def get_pending_issues(
    class_id: str = "",
    issue_service: IssueService = Depends(get_issue_service),
):
    """
    Lấy danh sách vấn đề đang chờ xử lý (OPEN + IN_PROGRESS) cho Dashboard GVCN.
    Kết quả đã được sắp xếp theo mức độ ưu tiên: URGENT → HIGH → MEDIUM → LOW.

    Tương đương renderAdvisorDashboard → issueService.getPendingIssues() trong main.py cũ.
    """
    print("[issues/pending] Đang truy xuất danh sách vấn đề chờ xử lý...")
    try:
        raw_issues = issue_service.getPendingIssues(advisorClassId=class_id)
    except Exception as e:
        print(f"[issues/pending] Lỗi truy xuất Firestore (DB fetch error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể truy xuất danh sách vấn đề. Vui lòng thử lại."
        )

    # Chuyển đổi từ dict thô sang schema IssueResponse
    issues_list = [
        IssueResponse(
            issue_id=issue.get("issue_id", ""),
            student_id=issue.get("student_id", "Ẩn danh"),
            chat_id=issue.get("chat_id"),
            intent=issue.get("intent"),
            sentiment=issue.get("sentiment"),
            priority=issue.get("priority", "LOW"),
            status=issue.get("status", "OPEN"),
            is_advisor_viewed=issue.get("is_advisor_viewed", False),
            unread_by_advisor=issue.get("unread_by_advisor", 0),
            unread_by_student=issue.get("unread_by_student", 0),
            created_at=str(issue.get("created_at", "")),
            updated_at=str(issue.get("updated_at", "")) if issue.get("updated_at") else None,
            title=issue.get("title"),
            category=issue.get("category"),
            content=issue.get("content"),
        )
        for issue in raw_issues
    ]

    print(f"[issues/pending] Tìm thấy {len(issues_list)} vấn đề chờ xử lý.")
    return PendingIssuesResponse(total=len(issues_list), issues=issues_list)


@router.patch("/{issue_id}/status", response_model=UpdateIssueStatusResponse)
async def update_issue_status(
    payload: UpdateIssueStatusRequest,
    issue_id: str = Path(..., description="ID phiếu vấn đề cần cập nhật"),
    issue_service: IssueService = Depends(get_issue_service),
):
    """
    Cập nhật trạng thái phiếu vấn đề (GVCN đánh dấu đã xử lý).

    Tương đương renderAdvisorDashboard → issueService.updateIssueStatus() trong main.py cũ.
    """
    # Kiểm tra giá trị hợp lệ
    if payload.new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Trạng thái không hợp lệ. Giá trị cho phép: {VALID_STATUSES}"
        )

    print(f"[issues/{issue_id}/status] Cập nhật trạng thái → {payload.new_status}")
    try:
        success = issue_service.updateIssueStatus(issue_id, payload.new_status)
    except Exception as e:
        print(f"[issues/{issue_id}/status] Lỗi cập nhật Firestore (DB update error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể cập nhật trạng thái. Vui lòng thử lại."
        )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy phiếu vấn đề với ID: {issue_id}"
        )

    return UpdateIssueStatusResponse(
        success=True,
        issue_id=issue_id,
        new_status=payload.new_status,
        message=f"Phiếu {issue_id} đã được chuyển sang trạng thái '{payload.new_status}'.",
    )


@router.post("/form", response_model=CreateIssueFromFormResponse, status_code=201)
async def create_issue_from_form(
    payload: CreateIssueFromFormRequest,
    issue_service: IssueService = Depends(get_issue_service),
):
    """
    Sinh viên chủ động nộp phiếu phản ánh vấn đề qua biểu mẫu (không qua chat AI).
    Hệ thống sẽ dùng thuật toán PriorityLogic để tự động phân loại và đánh giá mức độ khẩn cấp.
    """
    from app.features.issue_manager.PriorityLogic import PriorityLogic
    
    print(f"[issues/form] SV {payload.student_id} nộp phiếu: {payload.title}")
    
    try:
        # Tự động phân loại vấn đề
        logic = PriorityLogic()
        rawPriority, category, _ = logic.determinePriority(payload.content)
        
        # Ánh xạ từ P0/P1/P2 sang URGENT/HIGH/MEDIUM/LOW
        priority_map = {
            "P0": "URGENT",
            "P1": "HIGH",
            "P2": "MEDIUM",
            "INVALID": "LOW"
        }
        final_priority = priority_map.get(rawPriority, "LOW")
        
        ticket_id = issue_service.createIssueFromForm(
            studentId=payload.student_id,
            title=payload.title,
            category=category,
            priority=final_priority,
            content=payload.content,
        )
    except Exception as e:
        print(f"[issues/form] Lỗi tạo phiếu từ form (form submission error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể gửi phiếu phản ánh. Vui lòng thử lại."
        )

    if not ticket_id:
        raise HTTPException(
            status_code=500,
            detail="Tạo phiếu thất bại. Vui lòng liên hệ quản trị viên."
        )

    print(f"[issues/form] Phiếu tạo thành công: {ticket_id}")
    return CreateIssueFromFormResponse(
        success=True,
        issue_id=ticket_id,
        message="Phiếu phản ánh đã được gửi thành công. GVCN sẽ xem xét sớm nhất có thể.",
    )


# --- Messaging Endpoints ---

class MessageResponse(BaseModel):
    message_id: str
    issue_id: str
    sender_id: str
    sender_role: str
    content: str
    created_at: Optional[Any] = None

class AddMessageRequest(BaseModel):
    sender_id: str = Field(..., min_length=1)
    sender_role: str = Field(..., description="STUDENT or ADVISOR")
    content: str = Field(..., min_length=1)

class MarkReadRequest(BaseModel):
    reader_role: str = Field(..., description="STUDENT or ADVISOR")

@router.get("/{issue_id}/messages", response_model=List[MessageResponse])
async def get_issue_messages(
    issue_id: str = Path(...),
    issue_service: IssueService = Depends(get_issue_service),
):
    """Lấy danh sách tin nhắn của một phiếu vấn đề."""
    messages = issue_service.getIssueMessages(issue_id)
    result = []
    for m in messages:
        result.append(MessageResponse(
            message_id=m.get("message_id", ""),
            issue_id=m.get("issue_id", ""),
            sender_id=m.get("sender_id", ""),
            sender_role=m.get("sender_role", ""),
            content=m.get("content", ""),
            created_at=str(m.get("created_at", ""))
        ))
    return result

@router.post("/{issue_id}/messages", response_model=MessageResponse, status_code=201)
async def add_message_to_issue(
    payload: AddMessageRequest,
    issue_id: str = Path(...),
    issue_service: IssueService = Depends(get_issue_service),
):
    """Gửi tin nhắn mới vào phiếu."""
    if payload.sender_role not in ["STUDENT", "ADVISOR"]:
        raise HTTPException(status_code=422, detail="Vai trò không hợp lệ.")
        
    msg = issue_service.addMessageToIssue(issue_id, payload.sender_id, payload.sender_role, payload.content)
    if not msg:
        raise HTTPException(status_code=500, detail="Lỗi gửi tin nhắn.")
        
    return MessageResponse(
        message_id=msg.get("message_id", ""),
        issue_id=msg.get("issue_id", ""),
        sender_id=msg.get("sender_id", ""),
        sender_role=msg.get("sender_role", ""),
        content=msg.get("content", ""),
        created_at=str(msg.get("created_at", ""))
    )

@router.patch("/{issue_id}/read")
async def mark_issue_as_read(
    payload: MarkReadRequest,
    issue_id: str = Path(...),
    issue_service: IssueService = Depends(get_issue_service),
):
    """Đánh dấu phiếu đã đọc, reset số lượng tin chưa đọc."""
    if payload.reader_role not in ["STUDENT", "ADVISOR"]:
        raise HTTPException(status_code=422, detail="Vai trò không hợp lệ.")
        
    success = issue_service.markIssueAsRead(issue_id, payload.reader_role)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu hoặc lỗi server.")
        
    return {"success": True, "message": "Đã đánh dấu đọc."}

@router.get("/student/{student_id}", response_model=PendingIssuesResponse)
async def get_student_issues(
    student_id: str = Path(...),
    issue_service: IssueService = Depends(get_issue_service),
):
    """Lấy danh sách vấn đề do một sinh viên tạo."""
    try:
        raw_issues = issue_service.getStudentIssues(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi truy xuất danh sách vấn đề.")

    issues_list = [
        IssueResponse(
            issue_id=issue.get("issue_id", ""),
            student_id=issue.get("student_id", ""),
            chat_id=issue.get("chat_id"),
            intent=issue.get("intent"),
            sentiment=issue.get("sentiment"),
            priority=issue.get("priority", "LOW"),
            status=issue.get("status", "OPEN"),
            is_advisor_viewed=issue.get("is_advisor_viewed", False),
            unread_by_advisor=issue.get("unread_by_advisor", 0),
            unread_by_student=issue.get("unread_by_student", 0),
            created_at=str(issue.get("created_at", "")),
            updated_at=str(issue.get("updated_at", "")) if issue.get("updated_at") else None,
            title=issue.get("title"),
            category=issue.get("category"),
            content=issue.get("content"),
        )
        for issue in raw_issues
    ]

    return PendingIssuesResponse(total=len(issues_list), issues=issues_list)


