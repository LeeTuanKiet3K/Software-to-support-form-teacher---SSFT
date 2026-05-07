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
