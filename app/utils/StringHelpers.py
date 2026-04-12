import unicodedata
import re

def removeVietnameseAccents(text: str) -> str:
    """
    Chuyển tiếng Việt có dấu thành không dấu để hỗ trợ Search.
    """
    # Chuẩn hoá NFD biến chữ cái có dấu thành chữ cái thường và dấu
    m_normalized = unicodedata.normalize('NFD', text)
    # Lọc bỏ các dấu
    m_noAccents = "".join(c for c in m_normalized if not unicodedata.combining(c))
    # Thay thế thủ công ký tự Đ và đ
    m_noAccents = m_noAccents.replace("đ", "d").replace("Đ", "D")
    return m_noAccents

def extractKeywords(text: str) -> list:
    """
    Tách từ khóa chính để hỗ trợ AI Processor, bỏ qua dấu câu chuyên ngành.
    """
    # Xoá dấu câu, lấy từ dài hơn 2 ký tự làm từ khoá
    m_cleanText = re.sub(r'[^\w\s]', '', text)
    m_words = m_cleanText.split()
    m_keywords = [word.lower() for word in m_words if len(word) > 2]
    return list(set(m_keywords))
