from typing import Dict, List, Any
from app.services.FirestoreHandler import FirestoreHandler
from app.features.notifications.NotificationService import NotificationService
from app.core.Constants import WarningThresholds


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

        # 1: GPA thấp
        isLowScore: bool = currentGpa < WarningThresholds.GPA_WARNING

        if isLowScore:
            alerts.append("GPA dưới mức cảnh báo")

        # 2: GPA giảm mạnh
        if (prevGpa - currentGpa) >= WarningThresholds.GPA_DROP_WARNING:
            alerts.append("GPA giảm mạnh so với lần cập nhật trước")

        # 3: Rớt nhiều môn
        subjects: List[Dict[str, Any]] = afterData.get("subjects", [])

        failCount: int = sum(
            1 for subject in subjects
            if float(subject.get("score", 0)) < 5
        )

        if failCount >= WarningThresholds.MAX_FAILED_SUBJECTS:
            alerts.append("Rớt nhiều môn học")

        # Không có cảnh báo -> bỏ qua
        if not alerts:
            return

        # Kiểm tra trạng thái AI đã hỏi thăm chưa
        aiCheckSent: bool = afterData.get("ai_check_sent", False)

        # Nếu AI chưa hỏi thăm -> ưu tiên hỗ trợ sinh viên trước
        if not aiCheckSent:
            self.m_notificationService.sendStudentEncouragement(studentId)

            # Đánh dấu đã gửi hỏi thăm
            self.m_dbHandler.updateDocument(
                collectionName="Academic_records",
                documentId=studentId,
                data={
                    "is_low_score": isLowScore,
                    "ai_check_sent": True,
                    "student_responded": False
                }
            )

            return
        
         # Nếu GPA quá thấp -> warning cho GVCN
        if currentGpa < 1.5:
            self.m_notificationService.sendAcademicAlert(
                studentId,
                alerts
            )