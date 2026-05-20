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
    PENDING_ADVISOR = "PENDING_ADVISOR"  # Chờ GVCN xử lý
    PENDING_ADVISOR = "PENDING_ADVISOR"  # Chờ GVCN xử lý

class UserRole:
    """
    Vai trò người dùng trong hệ thống (User Roles).
    """
    STUDENT = "student"     # Sinh viên
    ADVISOR = "advisor"     # Cố vấn/Giáo viên chủ nhiệm
    ADMIN = "admin"         # Quản trị viên


class WarningThresholds:
    """
    Ngưỡng cảnh báo học vụ (AcademicObserver / Analytics).
    """
    GPA_WARNING = 2.0
    GPA_DROP_WARNING = 0.5
    MAX_FAILED_SUBJECTS = 2
    MAX_ABSENCES = 3