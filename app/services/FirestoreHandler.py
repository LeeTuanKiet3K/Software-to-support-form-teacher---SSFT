import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.Config import AppConfig

class FirestoreHandler:
    """
    Lớp xử lý kết nối và thao tác với Firestore (Firestore Handler Layer).
    Quản lý các thao tác CRUD tiêu chuẩn và tìm kiếm theo từ khóa (Keyword Search).
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ (Initialize services) Firestore.
        """
        self.m_serviceAccountPath = AppConfig.FIREBASE_SERVICE_ACCOUNT_JSON
        
        if not self.m_serviceAccountPath:
            raise ValueError("Error: FIREBASE_SERVICE_ACCOUNT_JSON not found in configuration.")
        
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)
        
        # Bản sao nội bộ, tuyệt đối không lộ (expose) ra ngoài để bảo mật
        self.m_db = firestore.client()

    def generateDocumentId(self, collectionName: str) -> str:
        """
        Tạo và trả về một ID chuẩn 20 ký tự của Firestore một cách an toàn
        mà không cần lộ client gốc ra bên ngoài.
        """
        return self.m_db.collection(collectionName).document().id

    def saveDocument(self, collectionName: str, data: Dict[str, Any], documentId: Optional[str] = None) -> str:
        """
        Lưu dữ liệu vào Firestore (Save document to Firestore).
        Tích hợp log vào AI_logs nếu có thao tác liên quan đến AI.
        """
        currentTime = datetime.now(timezone.utc)
        if "created_at" not in data:
            data["created_at"] = currentTime
        data["updated_at"] = currentTime
        collectionRef = self.m_db.collection(collectionName)
        
        if documentId:
            collectionRef.document(documentId).set(data)
            savedId = documentId
        else:
            _, docRef = collectionRef.add(data)
            savedId = docRef.id

        # Kiểm tra nếu là các thao tác liên quan đến AI để ghi log
        m_aiEventTriggers = ["AI_logs", "Common_data", "responses", "issues", "knowledge_base", "ai_responses", "chats"]
        if collectionName in m_aiEventTriggers:
            self.m_logAiAction("save_document", collectionName, savedId)

        return savedId

    def getDocument(self, collectionName: Optional[str] = None, documentId: Optional[str] = None, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Lấy dữ liệu từ Firestore (Retrieve document from Firestore).
        """
        if collectionName is None:
            collectionName = kwargs.get("collection")
        if documentId is None:
            documentId = kwargs.get("docId")

        if not collectionName or not documentId:
            return None

        docRef = self.m_db.collection(collectionName).document(documentId)
        doc = docRef.get()
        
        if doc.exists:
            docData = doc.to_dict()
            if docData:
                docData['id'] = doc.id
            if collectionName in ["Common_data", "AI_logs"]:
                self.m_logAiAction("get_document", collectionName, documentId)
            return docData
        return None

    def updateDocument(self, collectionName: str, documentId: str, data: Dict[str, Any]) -> bool:
        """
        Cập nhật dữ liệu vào Firestore (Update existing document).
        """
        docRef = self.m_db.collection(collectionName).document(documentId)
        try:
            docRef.update(data)
            if collectionName in ["Common_data", "AI_logs"]:
                self.m_logAiAction("update_document", collectionName, documentId)
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    def deleteDocument(self, collectionName: str, documentId: str) -> bool:
        """
        Xóa một document khỏi Firestore (Delete document).
        """
        docRef = self.m_db.collection(collectionName).document(documentId)
        try:
            docRef.delete()
            if collectionName in ["Common_data", "AI_logs"]:
                self.m_logAiAction("delete_document", collectionName, documentId)
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def m_logAiAction(self, action: str, targetCollection: str, targetId: str) -> None:
        """
        Hàm nội bộ (Private function) để ghi nhận nhật ký thao tác liên quan đến AI.
        """
        logData = {
            "action": action,
            "target_collection": targetCollection,
            "target_id": targetId,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        try:
            self.m_db.collection("AI_logs").add(logData)
        except Exception as e:
            print(f"Error writing AI log: {e}")

    def queryDocuments(self, collectionName: str, filters: List[Tuple[str, str, Any]], limitCount: int = 100) -> List[Dict[str, Any]]:
        """
        Truy vấn danh sách tài liệu dựa trên các bộ lọc (vd: array_contains_any).
        """
        query = self.m_db.collection(collectionName)

        for field, operator, value in filters:
            query = query.where(filter=firestore.FieldFilter(field, operator, value))

        query = query.limit(limitCount)

        resultList = []
        try:
            docs = query.stream()
            for doc in docs:
                docData = doc.to_dict()
                if docData is not None:
                    docData['id'] = doc.id
                    resultList.append(docData)
        except Exception as e:
            print(f"Error querying documents: {e}")
            
        return resultList

    def addDocument(self, collection: str, data: Dict[str, Any]) -> str:
        """Alias tương thích ngược cho saveDocument."""
        return self.saveDocument(collectionName=collection, data=data)

    def queryOne(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Truy vấn một document đầu tiên theo điều kiện bằng nhau."""
        result = self.queryDocuments(
            collectionName=collection,
            filters=[(field, "==", value)],
            limitCount=1,
        )
        return result[0] if result else None

    def getUserProfile(self, uid: str) -> Optional[Dict[str, Any]]:
        """Lấy hồ sơ người dùng theo UID từ collection Users."""
        return self.getDocument(collectionName="Users", documentId=uid)

    def createUserProfile(self, uid: str, profileData: Dict[str, Any]) -> bool:
        """Tạo hồ sơ người dùng theo UID vào collection Users."""
        try:
            self.saveDocument(collectionName="Users", data=profileData, documentId=uid)
            return True
        except Exception as error:
            print(f"Error creating user profile: {error}")
            return False