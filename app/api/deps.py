from app.services.FirestoreHandler import FirestoreHandler

def get_firestore_handler() -> FirestoreHandler:
    """Dependency cung cấp FirestoreHandler instance."""
    return FirestoreHandler()

def get_academic_service():
    """Dependency cung cấp AcademicService instance."""
    from app.features.academic.AcademicService import AcademicService
    return AcademicService()
