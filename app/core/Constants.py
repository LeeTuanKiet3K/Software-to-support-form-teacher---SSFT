class IssuePriority:
    """
    Mức độ ưu tiên của vấn đề (Issue Priority levels).
    """
    LOW = "LOW"             # Thấp
    MEDIUM = "MEDIUM"       # Trung bình
    HIGH = "HIGH"           # Cao
    URGENT = "URGENT"       # Khẩn cấp

class IssueStatus:
    """
    Trạng thái xử lý vấn đề (Issue Status).
    """
    OPEN = "OPEN"           # Mở / Chờ xử lý
    IN_PROGRESS = "IN_PROGRESS" # Đang xử lý
    RESOLVED = "RESOLVED"   # Đã giải quyết

class UserRole:
    """
    Vai trò người dùng trong hệ thống (User Roles).
    """
    STUDENT = "STUDENT"     # Sinh viên
    ADVISOR = "ADVISOR"     # Cố vấn/Giáo viên chủ nhiệm
