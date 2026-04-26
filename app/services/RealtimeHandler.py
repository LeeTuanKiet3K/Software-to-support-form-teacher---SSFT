from app.features.academic.AcademicObserver import AcademicObserver
from app.services.FirestoreHandler import FirestoreHandler


class RealtimeHandler:
    """
    RealtimeHandler (Lắng nghe thay đổi Firestore)
    """

    def __init__(self):
        self.m_observer = AcademicObserver()
        self.m_db = FirestoreHandler().getClient()

    def listenAcademicRecords(self) -> None:
        """
        Lắng nghe collection Academic_records
        """

        docs = self.m_db.collection("Academic_records")

        def onSnapshot(colSnapshot, changes, readTime):
            for change in changes:
                if change.type.name == "MODIFIED":
                    studentId = change.document.id
                    afterData = change.document.to_dict()

                    # ⚠️ hiện tại chưa có beforeData
                    self.m_observer.processAcademicUpdate(
                        studentId,
                        {},  
                        afterData
                    )

        docs.on_snapshot(onSnapshot)