class ROLES:
    """
    Các vai trò trong hệ thống.
    """
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class IssueStatus:
    """
    Các trạng thái của vấn đề.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"

class PriorityLevels:
    """
    Các mức độ ưu tiên của vấn đề.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class WarningThresholds:
    """
    Các ngưỡng cảnh báo học vụ.
    """
    GPA_WARNING = 2.0
    GPA_DROP_WARNING = 0.5
    MAX_FAILED_SUBJECTS = 2
    MAX_ABSENCES = 3