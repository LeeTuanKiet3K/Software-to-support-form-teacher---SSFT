import re
import html

def validateEmail(email: str) -> bool:
    """
    Kiểm tra định dạng email (ưu tiên email sinh viên nếu có domain cụ thể, ví dụ: @student.edu.vn).
    """
    emailRegex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(emailRegex, email) is not None

def validatePasswordStrength(password: str) -> bool:
    """
    Kiểm tra độ bảo mật mật khẩu (ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và chữ số).
    """
    if len(password) < 8:
        return False
    hasLower = re.search(r"[a-z]", password) is not None
    hasUpper = re.search(r"[A-Z]", password) is not None
    hasNumber = re.search(r"\d", password) is not None
    return hasLower and hasUpper and hasNumber

def isValidStudentId(mssv: str) -> bool:
    """
    Kiểm tra định dạng mã số sinh viên. 
    Giả sử định dạng chuẩn là chuỗi từ 8 đến 10 số.
    """
    return mssv.isdigit() and (8 <= len(mssv) <= 10)

def sanitizeText(text: str) -> str:
    """
    Làm sạch chuỗi để chống XSS/Injection.
    """
    # Xoá khoảng trắng thừa và escape mã HTML (Chống XSS)
    cleanText = text.strip()
    return html.escape(cleanText)
