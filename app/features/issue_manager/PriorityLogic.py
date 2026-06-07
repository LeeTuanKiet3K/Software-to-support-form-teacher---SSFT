# /app/features/issue_manager/PriorityLogic.py
import re
from typing import Tuple

class PriorityLogic:
    def __init__(self):
        # Khởi tạo các tập từ khóa dựa trên logic phân loại
        self.m_highKeywords = [
            "cảnh báo học vụ", "buộc thôi học", "quyết định đình chỉ", "tính lùi môn", 
            "không đủ điều kiện", "hết hạn đăng ký", "trầm cảm", "áp lực quá mức", 
            "không thể tiếp thu", "tự tử", "bỏ học", "bế tắc", "mất phương hướng", 
            "chọn chuyên ngành", "định hướng", "chọn sai ngành", "không hợp ngành", 
            "lệch tiến độ", "lời khuyên nghề nghiệp", "môi trường học tập",
            "học cải thiện", "học lại", "nợ môn", "rớt môn", "thi lại", "phúc khảo", 
            "gpa thấp", "bị hủy lớp", "trùng lịch học", "bảo lưu", "chuyển ngành", 
            "đổi ngành", "nghỉ học tạm thời", "tốt nghiệp muộn", "trễ tiến độ",
            "phương pháp tự học", "nghiên cứu khoa học", "học nhóm", "quản lý thời gian", 
            "clb học thuật", "lab nghiên cứu", "mentoring", "lộ trình 4 năm", 
            "bí quyết thủ khoa", "đạt học bổng", "tối ưu điểm số", "đồ án tốt nghiệp",
            "thực tập sinh", "internship", "làm CV", "portfolio", "chứng chỉ quốc tế", 
            "tiếng Anh đầu ra", "TOEIC", "IELTS", "kỹ năng mềm", "networking", 
            "kết nối doanh nghiệp", "hackathon", "cuộc thi công nghệ", "dự án thực tế", 
            "nhân sự chất lượng cao", "phỏng vấn tuyển dụng", "định hướng chuyên sâu"
        ]
        self.m_mediumKeywords = [
            "rớt môn", "nợ môn", "học lại", "chuyển ngành", "bảo lưu", "tai nạn", 
            "nhập viện", "công an", "bị lừa đảo", "mất xe", "học phí", "không có tiền", 
            "vay vốn", "gia đình khó khăn", "mất người thân"
            "thiếu điểm rèn luyện", "thiếu tín chỉ", "vi phạm quy chế", "đình chỉ thi", 
            "bị biên bản", "gpa sụt dốc", "không đủ điều kiện tốt nghiệp", "mất học bổng", 
            "bị lừa tiền cọc", "đa cấp lừa đảo", "lừa đảo việc làm", "ngộ độc thực phẩm", "ốm nặng", 
            "mất giấy tờ tùy thân", "mất căn cước", "phòng trọ bị trộm", "nợ học phí", 
            "bị khóa tài khoản học phí", "gia đình phá sản", "bị cô lập", "bị bắt nạt"
        ]
        self.m_lowKeywords = [
            "lịch học", "phòng học", "mật khẩu", "cách đóng tiền", "câu lạc bộ", 
            "giấy xác nhận", "thẻ sinh viên", "portal", "hcmus"
            "lịch thi", "phòng thi", "bảng điểm", "đăng ký môn", "rút môn học", 
            "hủy học phần", "thời hạn đóng học phí", "gia hạn đóng phí", "miễn giảm học phí", 
            "chuẩn đầu ra", "quy chế học vụ", "xét tốt nghiệp", "nhận bằng", "ký túc xá", "nội trú", 
            "bảo hiểm y tế", "bhy t", "thư viện", "tài khoản portal", "email sinh viên", "canvas", 
            "kích hoạt tài khoản", "cấp lại thẻ", "lịch sinh hoạt công dân"
        ]
        self.m_humanTouchKeywords = [
            "chán", "buồn ngủ", "mất động lực", "wifi yếu", "nóng quá", "không hợp bạn",
            "nản", "lười", "nhớ nhà", "cô đơn", "thất tình", "overload", "mệt mỏi", 
            "chán học", "deadline ngập đầu", "giảng viên khó tính", "thầy cô hắc ám", 
            "đồ ăn căng tin", "gửi xe lâu", "kẹt xe", "mưa to", "mất mạng", "điều hòa hỏng", 
            "hết chỗ ngồi", "đói bụng", "bài tập nhiều quá"
        ]
        self.m_spamKeywords = [
            "đùa đấy", "haha", "kkk", "test bot", "😂", "🤣", "asdasdasd", "123123",
            "qwert", "bbbbb", "111111", "@@@"
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