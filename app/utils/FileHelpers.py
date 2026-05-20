import os
import re
import uuid

def isAllowedExtension(fileName: str) -> bool:
    """
    Kiểm tra đuôi file (.jpg, .png, .pdf) có hợp lệ không.
    """
    m_allowedExtensions = [".jpg", ".jpeg", ".png", ".pdf"]
    _, ext = os.path.splitext(fileName.lower())
    return ext in m_allowedExtensions

def checkFileSize(fileSize: int, maxMb: int = 5) -> bool:
    """
    Kiểm tra dung lượng file có nằm trong giới hạn không.
    """
    maxBytes = maxMb * 1024 * 1024
    return fileSize <= maxBytes

def generateSafeFileName(studentId: str, originalName: str) -> str:
    """
    Tạo tên file an toàn để lưu trữ tự động.
    """
    _, ext = os.path.splitext(originalName.lower())
    m_safeUuid = str(uuid.uuid4())[:8]
    m_sanitizedStudentId = re.sub(r'[^a-zA-Z0-9]', '', studentId)
    
    return f"{m_sanitizedStudentId}_{m_safeUuid}{ext}"
