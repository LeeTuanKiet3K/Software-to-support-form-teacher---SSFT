from typing import List, Dict, Any

from app.services.FirestoreHandler import FirestoreHandler


class NotificationService:
    """
    NotificationService (Dịch vụ gửi thông báo)
    """

    def __init__(self) -> None:
        self.m_dbHandler: FirestoreHandler = FirestoreHandler()

    def sendStudentEncouragement(self, studentId: str) -> None:
        """
        AI chủ động hỏi thăm sinh viên khi phát hiện học vụ bất thường.

        Args:
            studentId (str): ID sinh viên.
        """

        # Lấy thông tin sinh viên
        student: Dict[str, Any] = self.m_dbHandler.getDocument(
            collection="Users",
            docId=studentId
        )

        if not student:
            return

        messageContent: str = (
            "Mình thấy điểm số gần đây của bạn đang ở mức khá thấp. "
            "Nếu bạn đang gặp khó khăn trong học tập hoặc cuộc sống, "
            "bạn có thể chia sẻ với mình nhé."
        )

        # Notification cho sinh viên
        self.m_dbHandler.addDocument(
            collection="Notifications",
            data={
                "user_id": studentId,
                "title": "AI Academic Support",
                "content": messageContent,
                "type": "system",
                "is_read": False
            }
        )

        # Lưu AI message vào hệ thống chat
        self.m_dbHandler.addDocument(
            collection="Messages",
            data={
                "chat_id": f"academic_support_{studentId}",
                "sender_id": "AI_SYSTEM",
                "message": messageContent,
                "is_ai": True
            }
        )

        # Ghi log hệ thống
        self.m_dbHandler.addDocument(
            collection="Audit_logs",
            data={
                "user_id": "system",
                "action": "ACADEMIC_ENCOURAGEMENT_SENT",
                "target_id": studentId,
                "metadata": {
                    "type": "low_gpa_support"
                }
            }
        )

    def sendAcademicAlert(self, studentId: str, alerts: List[str]) -> None:
        """
        Gửi cảnh báo học vụ đến GVCN.

        Args:
            studentId (str): ID sinh viên.
            alerts (List[str]): Danh sách cảnh báo.
        """

        # Lấy thông tin sinh viên
        student: Dict[str, Any] = self.m_dbHandler.getDocument(
            collection="Users",
            docId=studentId
        )

        if not student:
            return

        classId: str = student.get("class_id", "")

        # Tìm lớp → GVCN
        classData: Dict[str, Any] = self.m_dbHandler.queryOne(
            collection="Classes",
            field="class_name",
            value=classId
        )

        if not classData:
            return

        advisorId: str = classData.get("advisor_id", "")

        # Nội dung cảnh báo
        content: str = (
            f"Sinh viên {student.get('full_name')} gặp vấn đề học vụ: "
            f"{', '.join(alerts)}"
        )

        # Notification cho GVCN
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

        # Ghi log
        self.m_dbHandler.addDocument(
            collection="Audit_logs",
            data={
                "user_id": "system",
                "action": "ACADEMIC_ALERT",
                "target_id": studentId,
                "metadata": {
                    "alerts": alerts
                }
            }
        )