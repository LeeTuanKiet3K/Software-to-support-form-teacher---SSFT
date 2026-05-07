# /app/features/issue_manager/PriorityLogic.py
import re
from typing import Tuple

class PriorityLogic:
    def __init__(self):
        # Khởi tạo các tập từ khóa dựa trên logic phân loại
        self.m_highKeywords = [
            "cảnh báo học vụ", "buộc thôi học", "quyết định đình chỉ", "tính lùi môn", 
            "không đủ điều kiện", "hết hạn đăng ký", "cứu em", "trầm cảm", "áp lực quá mức", 
            "không thể tiếp thu", "tự tử", "bỏ học", "bế tắc", "mất phương hướng", 
            "chọn chuyên ngành", "định hướng", "chọn sai ngành", "không hợp ngành", 
            "lệch tiến độ", "lời khuyên nghề nghiệp"
        ]
        self.m_mediumKeywords = [
            "rớt môn", "nợ môn", "học lại", "chuyển ngành", "bảo lưu", "tai nạn", 
            "nhập viện", "công an", "bị lừa đảo", "mất xe", "học phí", "không có tiền", 
            "vay vốn", "gia đình khó khăn", "mất người thân"
        ]
        self.m_lowKeywords = [
            "lịch học", "phòng học", "mật khẩu", "cách đóng tiền", "câu lạc bộ", 
            "giấy xác nhận", "thẻ sinh viên"
        ]
        self.m_humanTouchKeywords = [
            "chán", "buồn ngủ", "mất động lực", "wifi yếu", "nóng quá", "không hợp bạn"
        ]
        self.m_spamKeywords = [
            "đùa đấy", "haha", "kkk", "test bot", "😂", "🤣", "asdasdasd", "123123"
        ]

    def calculateEmotionalIndex(self, text: str) -> float:
        # Tích hợp LLM để phân tích cảm xúc (Sentiment Analysis)
        return 0.5  

    def detectSpam(self, text: str) -> bool:
        # Nhận diện mâu thuẫn ngữ cảnh hoặc tin nhắn rác
        textLower = text.lower()
        return any(word in textLower for word in self.m_spamKeywords)

    def determinePriority(self, issueContent: str) -> Tuple[str, str, bool]:
        text = issueContent.lower()
        emotionalIndex = self.calculateEmotionalIndex(text)
        
        # 1. Lớp lọc xác thực Spam/Troll
        if self.detectSpam(text):
            return ("INVALID", "Spam", False)
        
        # 2. Mức ưu tiên cao (P0) - Fallback cho GVCN
        if any(word in text for word in self.m_highKeywords) or emotionalIndex >= 0.9:
            return ("P0", "High Risk", True)
        
        # 3. Mức ưu tiên trung bình (P1) - Fallback cho GVCN
        if any(word in text for word in self.m_mediumKeywords) or (0.6 <= emotionalIndex < 0.9):
            return ("P1", "Medium Risk", True)
        
        # 4. Mức ưu tiên thấp (P2) - Cần sự phản hồi tinh tế
        if any(word in text for word in self.m_humanTouchKeywords):
            return ("P2", "Pending Human Touch", True)
        
        # 5. Mức ưu tiên thấp (P2) - AI tự động giải quyết
        return ("P2", "General", False)


def classifyAndPrioritize(issueText: str):
    """
    Hàm wrapper tương thích cho module ChatProcessor cũ.
    """
    priorityLevel, category, isFallback = PriorityLogic().determinePriority(issueText)
    return {
        "priorityLevel": priorityLevel,
        "category": category,
        "isFallback": isFallback,
    }