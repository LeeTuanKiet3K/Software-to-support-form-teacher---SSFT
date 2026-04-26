from typing import List, Dict, Any
from app.services.FirestoreHandler import FirestoreHandler


class NotificationService:
    """
    NotificationService (Dịch vụ gửi thông báo)
    """

    def __init__(self) -> None:
        self.m_dbHandler: FirestoreHandler = FirestoreHandler()

    def sendAcademicAlert(self, studentId: str, alerts: List[str]) -> None:
        """
        Gửi cảnh báo học vụ đến GVCN

        :param studentId: ID sinh viên
        :param alerts: Danh sách cảnh báo
        """

        # 🔍 Lấy thông tin sinh viên
        student: Dict[str, Any] = self.m_dbHandler.getDocument(
            collection="Users",
            docId=studentId
        )

        if not student:
            return

        classId: str = student.get("class_id", "")

        # 🔍 Tìm lớp → GVCN
        classData: Dict[str, Any] = self.m_dbHandler.queryOne(
            collection="Classes",
            field="class_name",
            value=classId
        )

        if not classData:
            return

        advisorId: str = classData.get("advisor_id", "")

        # 📝 Tạo nội dung thông báo
        content: str = (
            f"Sinh viên {student.get('full_name')} gặp vấn đề: "
            f"{', '.join(alerts)}"
        )

        # 📬 Gửi notification
        self.m_dbHandler.addDocument(
            collection="Notifications",
            data={
                "user_id": advisorId,
                "title": "Cảnh báo học vụ",
                "content": content,
                "type": "system",
                "is_read": False
            }
        )

        # 📜 Ghi log hệ thống
        self.m_dbHandler.addDocument(
            collection="Audit_logs",
            data={
                "user_id": "system",
                "action": "ACADEMIC_ALERT",
                "target_id": studentId,
                "metadata": {"alerts": alerts}
            }
        )