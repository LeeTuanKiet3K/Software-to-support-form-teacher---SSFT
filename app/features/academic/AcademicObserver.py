from typing import Dict, List, Any
from app.services.FirestoreHandler import FirestoreHandler
from app.features.notifications.NotificationService import NotificationService


class AcademicObserver:
    """
    AcademicObserver (Bộ giám sát học vụ)
    Theo dõi sự thay đổi điểm số của sinh viên và phát hiện bất thường.
    """

    def __init__(self) -> None:
        self.m_dbHandler: FirestoreHandler = FirestoreHandler()
        self.m_notificationService: NotificationService = NotificationService()

    def processAcademicUpdate(
        self,
        studentId: str,
        beforeData: Dict[str, Any],
        afterData: Dict[str, Any]
    ) -> None:
        """
        Xử lý khi Academic_records thay đổi

        :param studentId: ID sinh viên
        :param beforeData: Dữ liệu trước khi update
        :param afterData: Dữ liệu sau khi update
        """

        prevGpa: float = float(beforeData.get("gpa", 0))
        currentGpa: float = float(afterData.get("gpa", 0))

        alerts: List[str] = []

        # Rule 1: GPA thấp
        if currentGpa < 2.0:
            alerts.append("GPA dưới 2.0")

        # Rule 2: GPA giảm mạnh
        if (prevGpa - currentGpa) >= 0.5:
            alerts.append("GPA giảm mạnh so với lần trước")

        # Rule 3: Rớt nhiều môn
        subjects: List[Dict[str, Any]] = afterData.get("subjects", [])
        failCount: int = sum(1 for s in subjects if float(s.get("score", 0)) < 5)

        if failCount >= 2:
            alerts.append("Rớt nhiều môn")

        # Nếu không có cảnh báo → bỏ qua
        if not alerts:
            return

        # Gửi cảnh báo cho GVCN
        self.m_notificationService.sendAcademicAlert(studentId, alerts)