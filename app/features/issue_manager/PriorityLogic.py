import re
from typing import TypedDict

class PriorityResult(TypedDict):
    """
    Kết quả trả về của quá trình phân loại và đánh giá mức độ ưu tiên.
    """
    priorityLevel: str
    isFallback: bool

def classifyAndPrioritize(issueText: str) -> PriorityResult:
    """
    Phân loại mức độ ưu tiên của vấn đề dựa trên danh sách từ khóa.
    
    Args:
        issueText (str): Nội dung vấn đề của sinh viên.
        
    Returns:
        PriorityResult: Dictionary chứa `priority_level` (P0, P1, P2) 
                        và cờ `is_fallback` (True/False).
    """
    # Chuyển đổi văn bản thành chữ thường để dễ dàng đối sánh từ khóa
    textLower = issueText.lower()
    
    # Danh sách từ khóa mức độ P0 (Critical - Cấp bách / Nhạy cảm / Tâm lý)
    p0Keywords = [
        r"\btự tử\b", r"\bchết\b", r"\btrầm cảm\b", 
        r"\bbạo lực\b", r"\bnghỉ học\b", r"\btuyệt vọng\b",
        r"\báp lực\b"
    ]
    
    # Danh sách từ khóa mức độ P1 (High - Khiếu nại / Vấn đề nghiêm trọng)
    p1Keywords = [
        r"\bkhiếu nại\b", r"\bbất công\b", r"\bsai điểm\b", 
        r"\bsai học phí\b", r"\bđổi giáo viên\b", r"\bphản ánh\b",
        r"\bbức xúc\b"
    ]
    
    # Kiểm tra mức độ P0
    for keyword in p0Keywords:
        if re.search(keyword, textLower):
            # Nếu chứa từ khóa nhạy cảm, đặt mức ưu tiên P0 và báo cần GVCN can thiệp (Fallback = True)
            return {
                "priorityLevel": "P0",
                "isFallback": True
            }
            
    # Kiểm tra mức độ P1
    for keyword in p1Keywords:
        if re.search(keyword, textLower):
            # Nếu chứa từ khóa khiếu nại, đặt mức ưu tiên P1 và báo cần GVCN can thiệp (Fallback = True)
            return {
                "priorityLevel": "P1",
                "isFallback": True
            }
            
    # Phần còn lại là P2 (Normal - Thông thường)
    # Các vấn đề thông thường AI có thể tự động trả lời, không cần GVCN can thiệp khẩn cấp (Fallback = False)
    return {
        "priorityLevel": "P2",
        "isFallback": False
    }
