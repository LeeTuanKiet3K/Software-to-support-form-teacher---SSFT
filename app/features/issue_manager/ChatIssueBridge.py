"""
Cầu nối lưu Issue từ kết quả PriorityLogic (Bridge từ issue_manager -> Firestore).
Không thay thế IssueService toàn cục; chỉ phục vụ luồng chat phân nhánh theo P0/P1/P2.
"""

from typing import Any, Dict, Optional

from firebase_admin import firestore

from app.core.Constants import IssuePriority, IssueStatus
from app.services.FirestoreHandler import FirestoreHandler


class ChatIssueBridge:
    """
    Tạo ticket Issues khi mức độ từ PriorityLogic đủ nặng để GVCN theo dõi.
    """

    def __init__(self) -> None:
        self.m_dbHandler = FirestoreHandler()

    def mapPriorityLevelToIssuePriority(self, priorityLevel: str) -> Optional[str]:
        """
        Ánh xạ P0/P1/P2/INVALID sang IssuePriority dùng trên dashboard.
        """
        mapping = {
            "P0": IssuePriority.URGENT,
            "P1": IssuePriority.HIGH,
            "P2": IssuePriority.MEDIUM,
            "INVALID": None,
        }
        return mapping.get(priorityLevel)

    def shouldCreateTicket(
        self,
        priorityLevel: str,
        isFallback: bool,
    ) -> bool:
        """
        Quyết định có ghi ticket hay không (giảm ticket rác).

        - INVALID: không tạo.
        - P0/P1: luôn tạo (cần GVCN nắm).
        - P2 + fallback (human touch): tạo ở mức MEDIUM.
        - P2 không fallback (general): không tạo (AI tự xử lý nhẹ).
        """
        if priorityLevel == "INVALID":
            return False
        if priorityLevel in ("P0", "P1"):
            return True
        if priorityLevel == "P2" and isFallback:
            return True
        return False

    def createIssueFromPriorityResult(
        self,
        chatId: str,
        studentId: str,
        rawMessage: str,
        priorityLevel: str,
        category: str,
        isFallback: bool,
    ) -> str:
        """
        Ghi một bản ghi Issues phản ánh đúng phân loại PriorityLogic.

        Lợi ích nghiệp vụ:
        - GVCN thấy đúng mức rủi ro (URGENT/HIGH/MEDIUM) trùng với thuật toán keyword/rủi ro.
        - Có audit trail: priority_level, category, đoạn tin nhắn rút gọn.

        Returns:
            Document ID hoặc chuỗi rỗng nếu bỏ qua.
        """
        if not self.shouldCreateTicket(priorityLevel, isFallback):
            return ""

        mapped = self.mapPriorityLevelToIssuePriority(priorityLevel)
        if not mapped:
            return ""

        preview = (rawMessage or "").strip()
        if len(preview) > 500:
            preview = preview[:497] + "..."

        studentProfile = self.m_dbHandler.queryOne("Users", "student_id", studentId)
        studentClassId = studentProfile.get("class_id", "") if studentProfile else ""

        issueData: Dict[str, Any] = {
            "chat_id": chatId,
            "student_id": studentId,
            "class_id": studentClassId,
            "priority": mapped,
            "status": IssueStatus.OPEN,
            "priority_level": priorityLevel,
            "category": category,
            "is_fallback": isFallback,
            "source": "priority_logic",
            "content": preview,
            "student_message_preview": preview,
            "is_advisor_viewed": False,
            "created_at": firestore.SERVER_TIMESTAMP,
        }

        try:
            return self.m_dbHandler.saveDocument("Issues", issueData)
        except Exception as error:
            print(f"Lỗi ghi Issues từ PriorityLogic (ChatIssueBridge): {error}")
            return ""
