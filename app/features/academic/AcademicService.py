from typing import Dict, Any

from app.services.FirestoreHandler import FirestoreHandler
from app.features.academic.AcademicObserver import AcademicObserver


class AcademicService:
    """
    AcademicService (Dịch vụ xử lý học vụ)
    """

    def __init__(self) -> None:
        self.m_dbHandler: FirestoreHandler = FirestoreHandler()
        self.m_observer: AcademicObserver = AcademicObserver()

    def inputGrade(self, data: Dict[str, Any]) -> bool:
        """
        Nhập hoặc cập nhật dữ liệu học vụ.

        Args:
            data (Dict): Dữ liệu học vụ.

        Returns:
            bool: Trạng thái xử lý thành công.
        """

        studentId: str = data.get("student_id", "")

        if not studentId:
            return False

        # Lấy dữ liệu cũ trước khi update
        beforeData: Dict[str, Any] = self.m_dbHandler.getDocument(
            collection="Academic_records",
            docId=studentId
        ) or {}

        # Kiểm tra document đã tồn tại chưa
        existingRecord = self.m_dbHandler.getDocument(
            collectionName="Academic_records",
            documentId=studentId
        )

        # Nếu đã tồn tại -> update
        if existingRecord:
            success: bool = self.m_dbHandler.updateDocument(
                collectionName="Academic_records",
                documentId=studentId,
                data=data
            )

        # Nếu chưa tồn tại -> create mới
        else:
            self.m_dbHandler.getClient() \
                .collection("Academic_records") \
                .document(studentId) \
                .set(data)

            success = True

        # Nếu lưu thất bại
        if not success:
            return False

        # Lấy dữ liệu sau khi update
        afterData: Dict[str, Any] = self.m_dbHandler.getDocument(
            collection="Academic_records",
            docId=studentId
        ) or {}

        # Kích hoạt observer để kiểm tra học vụ
        self.m_observer.processAcademicUpdate(
            studentId=studentId,
            beforeData=beforeData,
            afterData=afterData
        )

        return True