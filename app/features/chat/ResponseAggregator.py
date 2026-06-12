from typing import Dict, Any, List
from app.features.chat.ContextManager import ContextManager
from app.utils.StringHelpers import StringHelpers


class ResponseAggregator:
    """
    Bộ tổng hợp thông điệp (Response Aggregator).
    Đóng gói dữ liệu chat thành các Interface chuyên nghiệp cho UI sinh viên
    và trích xuất dữ liệu ẩn dành riêng cho bảng điều khiển Giáo viên (Advisor Dashboard).
    """

    def __init__(self) -> None:
        """
        Khởi tạo liên kết tới ContextManager để truy xuất lịch sử và tóm tắt hội thoại
        """
        self.m_contextManager = ContextManager()

    def formatFinalResponse(self, aiResponse: str, metadata: Dict[str, Any] = None) -> str:
        """
        Ghép câu trả lời từ AI (Groq) với các thông tin bổ trợ thành chuỗi hiển thị cuối cùng
        Biến câu trả lời thuần thành UI có định hướng hành động.

        Args:
            aiResponse (str): Câu trả lời thô từ AI (Groq).
            metadata (Dict): Dữ liệu bổ trợ — references, advisor_contact, v.v..

        Returns:
            str: Chuỗi hiển thị hoàn chỉnh đã được định dạng.
        """
        if not metadata:
            return aiResponse

        extraTexts = []

        # Đính kèm danh sách tài liệu tham khảo nếu tìm được nguồn liên quan
        references = metadata.get("references", [])
        if references:
            refStr = "\n\n **Tài liệu tham khảo/Biểu mẫu (References):**\n"
            for ref in references:
                refStr += f"- {ref}\n"
            extraTexts.append(refStr)

        # Gắn kèm thông tin liên hệ GVCN khi vấn đề cần can thiệp trực tiếp
        advisorContact = metadata.get("advisor_contact")
        if advisorContact:
            contactStr = f"\n\n **Trợ lý đề xuất hãy liên hệ trực tiếp GVCN:** {advisorContact}"
            extraTexts.append(contactStr)

        finalString = aiResponse + "".join(extraTexts)
        return finalString

    def generateQuickActions(self, intent: str) -> List[str]:
        if intent == "tam_ly":
            actions = ["Đặt lịch trò chuyện tín nhiệm", "Yêu cầu GVCN ẩn danh tĩnh"]
        elif intent == "khieu_nai":
            actions = ["Tải mẫu đơn 01-Form khiếu nại", "Xem lại quy chế phản hồi"]
        elif intent == "hoi_dap":
            actions = ["Truy cập sổ tay thủ tục sinh viên", "Xem điểm học tập"]
        else:
            actions = ["Chuyển trang chính", "Kết nối trực tiếp hỗ trợ viên"]

        return actions

    def createSummaryForAdvisor(self, chatId: str) -> Dict[str, str]:
        secretSummary = self.m_contextManager.summarizeOldContext(chatId)

        # Fallback thủ công khi AI (Groq) chưa kích hoạt tóm tắt
        if not secretSummary:
            recentHistory = self.m_contextManager.getChatContext(chatId, limit=2)
            if recentHistory:
                # Lấy tin nhắn cuối cùng của sinh viên làm nội dung tóm tắt 
                userInputs = [m['content'] for m in recentHistory if m['role'] == 'user']
                secretSummary = "Trọng tâm vừa thảo luận: " + StringHelpers.cleanText(
                    userInputs[-1] if userInputs else "N/A"
                )
            else:
                secretSummary = "Tiến trình chưa ghi nhận câu hỏi cụ thể."

        reportObj = {
            "chat_id": chatId,
            "secret_summary": secretSummary,
            "privacy_tag": "ADVISOR_ONLY",
        }

        return reportObj