import secrets
import string

def generateTempPassword(length: int = 10) -> str:
    """
    Tạo mật khẩu tạm thời ngẫu nhiên và an toàn.
    """
    m_alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(m_alphabet) for _ in range(length))
        # Đảm bảo mật khẩu đáp ứng đủ độ khó: có chữ thường, chữ hoa và số
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)):
            break
            
    return password
