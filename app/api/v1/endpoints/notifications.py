from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.features.notifications.NotificationService import NotificationService

router = APIRouter()


def get_notification_service() -> NotificationService:
    """Dependency cung cấp NotificationService instance."""
    return NotificationService()


class AcademicAlertRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="UID sinh viên")
    alerts: List[str] = Field(default_factory=list, description="Danh sách cảnh báo học vụ")


class NotificationActionResponse(BaseModel):
    success: bool
    message: str


class NotificationSummaryResponse(BaseModel):
    advisor_id: str
    total_unread: int
    latest_title: Optional[str] = None


@router.get("/summary/{advisor_id}", response_model=NotificationSummaryResponse)
async def get_notification_summary(
    advisor_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Endpoint mẫu tổng hợp thông báo.
    Lưu ý: Service hiện tại chưa có hàm query danh sách thông báo,
    nên trả về mẫu để đảm bảo contract API.
    """
    _ = notification_service
    return NotificationSummaryResponse(
        advisor_id=advisor_id,
        total_unread=0,
        latest_title=None,
    )


@router.post("/academic-alert", response_model=NotificationActionResponse, status_code=201)
async def create_academic_alert(
    payload: AcademicAlertRequest,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Tạo cảnh báo học vụ qua NotificationService."""
    notification_service.sendAcademicAlert(
        studentId=payload.student_id,
        alerts=payload.alerts,
    )
    return NotificationActionResponse(
        success=True,
        message="Đã gửi cảnh báo học vụ tới GVCN (nếu tìm thấy dữ liệu lớp).",
    )

from app.services.IssueService import IssueService
import uuid
from app.utils.DateHelpers import formatTimestamp

@router.get("/list")
async def get_notification_list(class_id: str = ""):
    issue_service = IssueService()
    try:
        issues = issue_service.getPendingIssues(advisorClassId=class_id)
    except Exception:
        issues = []
        
    notifications = []
    
    for issue in issues:
        # Check for unread issue
        if not issue.get("is_advisor_viewed", False):
            time_str = formatTimestamp(issue.get("created_at"))
            if not time_str:
                time_str = "Vừa xong"
            notifications.append({
                "id": str(uuid.uuid4()),
                "title": f"Phiếu mới: {issue.get('title', 'Chưa có tiêu đề')}",
                "desc": f"Sinh viên {issue.get('student_id', 'Ẩn danh')} vừa tạo phiếu phản ánh.",
                "time": time_str,
                "type": "urgent" if issue.get("priority") == "URGENT" else "system",
                "read": False,
                "url": f"/dashboard?issue={issue.get('issue_id')}"
            })
        elif issue.get("unread_by_advisor", 0) > 0:
            time_str = formatTimestamp(issue.get("updated_at") or issue.get("created_at"))
            if not time_str:
                time_str = "Vừa xong"
            notifications.append({
                "id": str(uuid.uuid4()),
                "title": "Tin nhắn mới",
                "desc": f"Có {issue.get('unread_by_advisor')} tin nhắn chưa đọc từ sinh viên {issue.get('student_id', 'Ẩn danh')}.",
                "time": time_str,
                "type": "message",
                "read": False,
                "url": f"/dashboard?issue={issue.get('issue_id')}"
            })
            
            
    return {"notifications": notifications}


class BroadcastRequest(BaseModel):
    advisor_id: str
    class_id: str
    title: str
    content: str

@router.post("/broadcast", response_model=NotificationActionResponse, status_code=201)
async def broadcast_announcement(
    payload: BroadcastRequest,
    notification_service: NotificationService = Depends(get_notification_service),
):
    count = notification_service.sendClassAnnouncement(
        advisorId=payload.advisor_id,
        classId=payload.class_id,
        title=payload.title,
        content=payload.content,
    )
    return NotificationActionResponse(
        success=True,
        message=f"Đã gửi thông báo tới {count} sinh viên."
    )

@router.get("/student/{student_id}")
async def get_student_notifications(student_id: str):
    from app.services.FirestoreHandler import FirestoreHandler
    db = FirestoreHandler()
    filters = [("user_id", "==", student_id)]
    notifications = db.queryDocuments(collectionName="Notifications", filters=filters, limitCount=50)
    
    result = []
    for n in notifications:
        time_str = formatTimestamp(n.get("created_at"))
        if not time_str:
            time_str = "Vừa xong"
        result.append({
            "id": n.get("id"),
            "title": n.get("title", "Thông báo mới"),
            "desc": n.get("content", ""),
            "time": time_str,
            "type": n.get("type", "system"),
            "read": n.get("is_read", False),
        })
    
    # Sắp xếp thô để thông báo mới nhất lên trên
    result.reverse()
    return {"notifications": result}

@router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    from app.services.FirestoreHandler import FirestoreHandler
    db = FirestoreHandler()
    db.updateDocument("Notifications", notification_id, {"is_read": True})
    return {"success": True}

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    from app.services.FirestoreHandler import FirestoreHandler
    db = FirestoreHandler()
    db.deleteDocument("Notifications", notification_id)
    return {"success": True}
