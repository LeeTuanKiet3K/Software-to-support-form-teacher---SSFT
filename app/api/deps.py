from app.services.FirestoreHandler import FirestoreHandler


def get_firestore_handler() -> FirestoreHandler:
    """Dependency cung cấp FirestoreHandler instance."""
    return FirestoreHandler()


def get_academic_service():
    """Dependency cung cấp AcademicService instance."""
    from app.features.academic.AcademicService import AcademicService
    return AcademicService()


def get_issue_service():
    """Dependency cung cấp IssueService instance (quản lý vấn đề sinh viên)."""
    from app.services.IssueService import IssueService
    return IssueService()


def get_middleware():
    """Dependency cung cấp Middleware instance (AI pipeline Llama + Gemini)."""
    from app.core.Middleware import Middleware
    return Middleware()


def get_orchestrator():
    """Dependency cung cấp ChatOrchestrator instance (điều phối luồng chat theo tier)."""
    from app.features.chat.ChatOrchestrator import ChatOrchestrator
    return ChatOrchestrator()


def get_aggregator():
    """Dependency cung cấp ResponseAggregator instance (tóm tắt chat cho GVCN)."""
    from app.features.chat.ResponseAggregator import ResponseAggregator
    return ResponseAggregator()


def get_auth_handler():
    """Dependency cung cấp FirebaseAuthHandler instance (xác thực và đăng xuất)."""
    from app.services.FirebaseAuthHandler import FirebaseAuthHandler
    return FirebaseAuthHandler()

def get_calendar_service():
    """Dependency cung cấp CalendarService instance."""
    from app.services.CalendarService import CalendarService
    return CalendarService()
