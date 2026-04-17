from typing import Dict, Any, List
from app.features.chat.ContextManager import ContextManager
from app.utils.StringHelpers import StringHelpers

class ResponseAggregator:
    """
    Bộ tổng hợp thông điệp (Response Aggregator).
    Đóng gói dữ liệu chat thành các Interface chuyên nghiệp cho AI
    và trích xuất dữ liệu ẩn cho phía Giáo viên (Dashboard).
    """

    def __init__(self) -> None:
        """Khởi tạo phiên bản hợp nhất ContextManager để truy xuất lõi AI tóm tắt."""
        self.m_contextManager = ContextManager()

    def formatFinalResponse(self, aiResponse: str, metadata: Dict[str, Any] = None) -> str:
        """
        Kết hợp câu trả lời từ Gemini với các thông tin bổ trợ (Final Output Formatting).
        Giúp giao diện sinh viên trở nên trực quan và có định hướng (Actionable UI).
        
        Args:
            aiResponse (str): Kết quả suy luận văn bản thô từ Cloud Gemini.
            metadata (Dict): Chứa dữ liệu ngoại vi (link tài liệu, info GVCN).
            
        Returns:
            str: Khối Markdown hoàn chỉnh đóng đính kèm.
        """
        if not metadata:
            return aiResponse
            
        extraTexts = []
        
        # Đóng đính kèm tài liệu bảo trợ tri thức (References Support)
        references = metadata.get("references", [])
        if references:
            refStr = "\n\n📋 **Tài liệu tham khảo/Biểu mẫu (References):**\n"
            for ref in references:
                refStr += f"- {ref}\n"
            extraTexts.append(refStr)
            
        # Gắn kèm thông tin cố vấn học tập trong rủi ro (Advisor Fallback Logic)
        advisorContact = metadata.get("advisor_contact")
        if advisorContact:
            contactStr = f"\n\n👨‍🏫 **Trợ lý đề xuất hãy liên hệ trực tiếp GVCN:** {advisorContact}"
            extraTexts.append(contactStr)
            
        # Tổng hợp các Block
        finalString = aiResponse + "".join(extraTexts)
        return finalString

    def generateQuickActions(self, intent: str) -> List[str]:
        """
        Dựa vào Intent phân loại bởi Llama 3 để đề xuất thẻ bấm thao tác nhanh (Quick Actions).
        Chuyển đổi luồng người dùng thành Actions ngay trong Chat UI.
        
        Args:
            intent (str): Nhóm ý định sinh viên (vd: tam_ly, khieu_nai, hoi_dap).
            
        Returns:
            List[str]: Nút bấm gắn trên Streamlit UI.
        """
        actions = []
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
        """
        Tổng hợp tóm tắt bí mật (Secret Summary) hiển thị ẩn ở giao diện của Giáo viên.
        Đảm bảo học sinh không có quyền truy xuất (Privacy Check), chống rò rỉ (Information Leakage).
        
        Args:
            chatId (str): Định danh luồng chat.
            
        Returns:
            Dict[str, str]: Gói Metadata bí mật của hội thoại để đưa vào IssueService.
        """
        # Sử dụng chức năng chạy nền Gemini từ ContextManager (Summary Inference)
        secretSummary = self.m_contextManager.summarizeOldContext(chatId)
        
        # Nếu chưa đủ dài để Gemini chạy tóm tắt (Fail-safe Fallback)
        if not secretSummary:
            recentHistory = self.m_contextManager.getChatContext(chatId, limit=2)
            if recentHistory:
                userInputs = [m['content'] for m in recentHistory if m['role'] == 'user']
                secretSummary = "Trọng tâm vừa thảo luận: " + StringHelpers.cleanText(userInputs[-1] if userInputs else "N/A")
            else:
                secretSummary = "Tiến trình chưa ghi nhận câu hỏi cụ thể."

        reportObj = {
            "chat_id": chatId,
            "secret_summary": secretSummary,
            "privacy_tag": "ADVISOR_ONLY",  # Cờ bảo vệ ngăn dữ liệu bị load nhầm ở frontend học sinh
        }
        
        return reportObj
